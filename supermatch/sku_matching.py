import itertools
import networkx as nx
from tqdm import tqdm
import logging
import collections
import operator
import random

import constants as keys
import services
from .clean_name import tokenize, add_clean_name


class SKUGraphCreator(services.GenericGraph):
    """ Create a graph with items as vertices and barcodes as edges """

    def __init__(self, id_doc_pairs):
        super().__init__()
        self.sku_graph = nx.Graph()
        self.connected_ids = set()
        self.id_doc_pairs = id_doc_pairs
        self.stages = dict()

    def init_sku_graph(self):
        # add all items as nodes
        print("init sku graph..")
        for doc_id in self.id_doc_pairs.keys():
            self.sku_graph.add_node(doc_id)

    def barcode_match(self):
        barcode_id_pairs = collections.defaultdict(set)
        for doc_id, doc in self.id_doc_pairs.items():
            barcodes = doc.get(keys.BARCODES, [])
            if not barcodes:
                continue

            market = doc.get(keys.MARKET)
            if market in {keys.GOOGLE}:
                pass

            for code in barcodes:
                barcode_id_pairs[code].add(doc_id)

        logging.info(f"adding_edges using {len(barcode_id_pairs)} barcodes")
        for ids in tqdm(barcode_id_pairs.values()):
            edges = itertools.combinations(ids, 2)
            self.sku_graph.add_edges_from(edges)
            self.connected_ids.update(ids)

        self.stages = {**dict.fromkeys(self.connected_ids, "barcode")}

    @staticmethod
    def get_promoted_links(promoted: dict) -> list:
        promoted_links = []
        for promoted_name, link in promoted.items():
            if any(
                    [
                        market_name in promoted_name
                        for market_name in keys.ALLOWED_MARKET_LINKS
                    ]
            ):
                if link[-1] == "/":
                    link = link[:-1]

                if "&gclid" in link:
                    link = link.split("&gclid")[0]
                if "?gclid" in link:
                    link = link.split("?gclid")[0]
                if "?utm" in link:
                    link = link.split("?utm")[0]
                if "&utm" in link:
                    link = link.split("&utm")[0]

                link = link.strip()
                promoted_links.append(link)

        return promoted_links

    def promoted_match(self):

        link_id_pairs = dict()
        for doc_id, doc in self.id_doc_pairs.items():
            link_id_pairs[doc.get(keys.LINK)] = doc_id

        promoted_connections = dict()
        refers_to_multiple_barcodes = set()

        for doc_id, doc in tqdm(self.id_doc_pairs.items()):
            promoted = doc.get(keys.PROMOTED, {})
            if not promoted:
                continue
            promoted_links = self.get_promoted_links(promoted)
            promoted_links = [link for link in promoted_links if link in link_id_pairs]

            # add edge iff sizes are the same
            referenced_ids = [link_id_pairs.get(link) for link in promoted_links]

            # promoted link artık sadece barcode u olmayanları bir gruba bağlıyor
            filtered_referenced_ids = [
                id
                for id in referenced_ids
                if not self.id_doc_pairs.get(id, {}).get(keys.BARCODES)
            ]

            # bir linki birden fazla link promote ediyorsa, hiçbiri dikkate alınmıyor
            for id in filtered_referenced_ids:
                if id in promoted_connections:
                    refers_to_multiple_barcodes.add(id)
                else:
                    promoted_connections[id] = doc_id

        promoted_connections = {
            id: doc_id
            for id, doc_id in promoted_connections.items()
            if id not in refers_to_multiple_barcodes and id not in self.connected_ids
        }

        for id, doc_id in promoted_connections.items():
            self.sku_graph.add_edge(id, doc_id)
            self.connected_ids.add(id)
            self.stages[id] = "promoted"

    def match_singles(self, id, name):
        """ connect single name to a group """

        token_set = tokenize(name)
        candidate_groups = [self.inverted_index.get(token, []) for token in token_set]
        candidate_groups = set(itertools.chain(*candidate_groups))
        if not candidate_groups:
            return

        matches = set()

        for id_group in candidate_groups:
            group_common = self.common_tokens.get(id_group, set())
            if not group_common:
                continue
            if token_set.issuperset(group_common):
                group_all = self.group_tokens.get(id_group, set())

                if group_all.issuperset(token_set):
                    common_set_size, diff_size = (
                        len(group_common),
                        len(group_all.difference(token_set)),
                    )
                    # first common, if commons same, difference
                    matches.add(
                        (
                            common_set_size,
                            diff_size,
                            id,
                            id_group,
                            tuple(group_common),
                            tuple(group_all.difference(token_set)),
                            name,
                            tuple(self.group_names.get(id_group)),
                        )
                    )
        if matches:
            max_common_size = max(matches, key=operator.itemgetter(0))[0]
            matches_with_max_common_size = [
                match for match in matches if match[0] == max_common_size
            ]
            if len(matches_with_max_common_size) > 1:
                match = min(matches_with_max_common_size, key=operator.itemgetter(1))
            else:
                match = matches_with_max_common_size.pop()

            (
                common_set_size,
                diff_size,
                id,
                id_group,
                common_set,
                diff_set,
                name,
                group_names,
            ) = match

            self.sku_graph.add_edges_from([(id, id_group[0])])
            self.connected_ids.add(id)
            self.stages[id] = "set_match"

            return name, group_names, common_set, diff_set

    def set_match(self):
        id_groups = self.create_connected_component_groups(self.sku_graph)

        # filter without barcode
        id_groups = [
            id_group
            for id_group in id_groups
            if all(id in self.connected_ids for id in id_group)  # len(id_group)>1 and
        ]

        common_tokens = dict()
        group_tokens = dict()
        self.inverted_index = collections.defaultdict(set)
        self.group_names = dict()

        add_clean_name(self.id_doc_pairs)

        logging.info("creating inverted index..")
        for id_group in tqdm(id_groups):
            names = [
                self.id_doc_pairs.get(id).get("clean_name")
                for id in id_group
                if "clone" not in id
            ]
            names = [n for n in names if n]
            self.group_names[tuple(id_group)] = names
            token_sets = [tokenize(name) for name in names]
            if token_sets:
                commons = set.intersection(*token_sets)
                common_tokens[tuple(id_group)] = commons
                all_tokens = set.union(*token_sets)
                group_tokens[tuple(id_group)] = all_tokens
                for token in all_tokens:
                    self.inverted_index[token].add(tuple(id_group))

        # filter empty sets
        self.common_tokens = {k: v for k, v in common_tokens.items() if v}
        self.group_tokens = {k: v for k, v in group_tokens.items() if v}

        unmatched_ids = set(self.id_doc_pairs.keys()).difference(self.connected_ids)
        single_names = [
            (id, self.id_doc_pairs.get(id).get("clean_name"))
            for id in unmatched_ids
            if "clone" not in id
        ]
        logging.info("matching singles..")
        # this could be parallel
        matched_names = [
            self.match_singles(id, name) for id, name in tqdm(single_names) if name
        ]
        matched_names = [m for m in matched_names if m]

        logging.info("saving matched_names..")
        services.save_json("matched_names.json", matched_names)

    def exact_name_match(self):
        """ merge barcode-less items with the same name """
        name_barcode_pairs = collections.defaultdict(set)
        name_id_pairs = collections.defaultdict(set)
        for doc_id, doc in self.id_doc_pairs.items():
            name = doc.get("clean_name")
            if not name:
                continue
            sorted_name = " ".join(sorted(name.split()))
            barcodes = doc.get(keys.BARCODES, [])
            name_barcode_pairs[sorted_name].update(set(barcodes))
            name_id_pairs[sorted_name].add(doc_id)

        for name, barcodes in name_barcode_pairs.items():
            if len(barcodes) <= 1:
                doc_ids = name_id_pairs.get(name)
                single_doc_ids = [id for id in doc_ids if id not in self.connected_ids]
                if len(single_doc_ids) > 1:
                    edges = itertools.combinations(single_doc_ids, 2)
                    self.sku_graph.add_edges_from(edges)
                    self.stages.update({**dict.fromkeys(single_doc_ids, "exact_name")})
                    self.connected_ids.update(single_doc_ids)

    def test_set_match(self):
        id_groups = self.create_connected_component_groups(self.sku_graph)
        id_groups = [
            [id for id in id_group if "clone" not in id] for id_group in id_groups
        ]
        id_groups = [g for g in id_groups if len(g) >= 3]

        # select 1 from a group, remove the edge, remove from connected, and later check if its matched
        expected_neighbors = {}
        for g in id_groups:
            sample_size = 1 if len(g) < 5 else 2
            test_nodes = random.sample(g, sample_size)
            for test_node in test_nodes:
                g.remove(test_node)
                self.connected_ids.remove(test_node)
                edges_of_test_node = self.sku_graph.edges(test_node)
                self.sku_graph.remove_edges_from(list(edges_of_test_node))

            for test_node in test_nodes:
                expected_neighbors[test_node] = g

        self.exact_name_match()
        self.set_match()

        ok = set()
        matched_to_another_group = set()
        id_groups = self.create_connected_component_groups(self.sku_graph)
        for g in id_groups:
            for node in g:
                if node in expected_neighbors:
                    expected = expected_neighbors.get(node)
                    if set(g).issuperset(set(expected)):
                        expected_neighbors.pop(node)
                        ok.add(node)
                    else:
                        matched_to_another_group.add(node)

        # the remaining in check_table failed
        logging.info(f"{len(ok)} is ok, {len(expected_neighbors)} is failed")

        def get_name_and_cleaned_name(id):
            doc = self.id_doc_pairs.get(id)
            name = doc.get("name")
            clean_name = doc.get("clean_name")
            return (name, clean_name)

        failed_names = {}
        for test_node_id, group in expected_neighbors.items():
            if test_node_id in matched_to_another_group:
                continue
            group_names = tuple(get_name_and_cleaned_name(id) for id in group)
            failed_names[str(get_name_and_cleaned_name(test_node_id))] = group_names

        services.save_json("failed_names.json", failed_names)

    def create_graph(self, debug=False):
        self.init_sku_graph()

        print("barcode match..")
        self.barcode_match()

        if debug:
            self.test_set_match()
        else:
            print("exact_name_match..")
            self.exact_name_match()

            print("set match..")
            self.set_match()

        print("promoted match..")
        self.promoted_match()

        return self.sku_graph, self.stages
