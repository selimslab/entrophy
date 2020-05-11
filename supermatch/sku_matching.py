import itertools
import networkx as nx
from tqdm import tqdm
import logging
import collections
import operator
import random

import constants as keys
from services import GenericGraph
import services
from services.size_finder import size_finder, SizingException
import multiprocessing


def tokenize(s):
    stopwords = {"ml", "gr", "adet", "ve", "and", "ile"}
    try:
        tokens = set(t for t in s.split() if t not in stopwords)
        tokens = set(t for t in tokens if len(t) > 1 or t.isdigit())
        return tokens
    except AttributeError as e:
        logging.error(e)
        return set()


def replace_size(id, name):
    name = services.clean_name(name)
    if not name:
        return

    digits = unit = size_match = None
    try:
        digits, unit, size_match = size_finder.get_digits_unit_size(name)
        name = name.replace(size_match, str(digits) + " " + unit)
    except SizingException:
        pass
    finally:
        # only size can have .
        tokens = []
        for t in name.split():
            if len(t) <= 1:
                continue
            if not t.replace(".", "").isdigit():
                tokens.append(t.replace(".", " "))
            else:
                tokens.append(t)

        name = " ".join(tokens)
        return id, name, digits, unit, size_match


def add_clean_name(id_doc_pairs):
    logging.info("add_clean_name..")

    to_clean = list()
    for doc_id, doc in id_doc_pairs.items():
        if "name" in doc and "clean_name" not in doc:
            to_clean.append((doc_id, doc.get("name")))

    with multiprocessing.Pool(processes=2) as pool:
        results = pool.starmap(replace_size, tqdm(to_clean))
        results = (r for r in results if r)
        for doc_id, clean_name, digits, unit, size_match in results:
            info = {
                "clean_name": clean_name,
                keys.DIGITS: digits,
                keys.UNIT: unit,
                keys.SIZE: size_match,
            }
            id_doc_pairs[doc_id].update(info)


class SKUGraphCreator(GenericGraph):
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

        relax = True
        for id_group in candidate_groups:
            group_common = self.common_tokens.get(id_group, set())
            if not group_common:
                continue
            if token_set.issuperset(group_common):
                group_all = self.group_tokens.get(id_group, set())

                include = False
                if group_all.issuperset(token_set):
                    include = True

                if relax:

                    relaxed_token_set = set(
                        t for t in token_set if len(t) > 2 or t.isdigit()
                    )
                    relaxed_token_set_size = len(relaxed_token_set)

                    if (
                            len(group_all.intersection(relaxed_token_set))
                            == relaxed_token_set_size
                    ):
                        print("r1", token_set, relaxed_token_set, group_all)
                        include = True
                    if not include:
                        relaxed_match_size = sum(
                            1
                            if token in group_all
                               or (
                                       len(token) > 3
                                       and any(token in t or t in token for t in group_all)
                               )
                            else 0
                            for token in relaxed_token_set
                        )

                        if relaxed_match_size == relaxed_token_set_size:
                            print("r2", token_set, relaxed_token_set, group_all)
                            include = True

                if include:
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

        print("id_groups", id_groups)
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

    def create_graph(self, debug=True):
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
