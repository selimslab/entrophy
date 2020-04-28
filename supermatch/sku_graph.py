import itertools
import networkx as nx
from tqdm import tqdm
import logging
import collections

import constants as keys
from services import GenericGraph
import services
from services.sizing.main import size_finder, SizingException


class SKUGraphCreator(GenericGraph):
    """ Create a graph with items as vertices and barcodes as edges """

    def __init__(self):
        super().__init__()
        self.sku_graph = nx.Graph()
        self.connected_ids = set()

    def _init_sku_graph(self, id_doc_pairs):
        # add all items as nodes
        print("creating sku graph..")
        for doc_id in id_doc_pairs.keys():
            self.sku_graph.add_node(doc_id)

    def barcode_match(self, id_doc_pairs: dict):
        barcode_id_pairs = collections.defaultdict(list)
        for doc_id, doc in id_doc_pairs.items():
            barcodes = doc.get(keys.BARCODES, [])
            if not barcodes:
                continue

            market = doc.get(keys.MARKET)
            if market in {keys.GOOGLE}:
                pass

            for code in barcodes:
                barcode_id_pairs[code] += doc_id

        logging.info(f"adding_edges using {len(barcode_id_pairs)} barcodes")
        for ids in barcode_id_pairs.values():
            edges = itertools.combinations(ids, 2)
            self.sku_graph.add_edges_from(edges)
            self.connected_ids.update(ids)

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

    def promoted_match(self, id_doc_pairs):
        logging.info("addding_edges_from_promoted_links..")

        link_id_pairs = dict()
        for doc_id, doc in id_doc_pairs.items():
            link_id_pairs[doc.get(keys.LINK)] = doc_id

        promoted_connections = dict()
        refers_to_multiple_barcodes = set()

        for doc_id, doc in tqdm(id_doc_pairs.items()):
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
                if not id_doc_pairs.get(id, {}).get(keys.BARCODES)
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
        matched_using_promoted = set(promoted_connections.keys())

        for id, doc_id in promoted_connections.items():
            self.sku_graph.add_edge(id, doc_id)
            self.connected_ids.add(id)

        return matched_using_promoted

    def _add_edges_from_exact_name_match(self, exact_match_groups: list):
        print("adding_edges_from_exact_name_match..")
        for ids in exact_match_groups:
            edges = itertools.combinations(ids, 2)
            self.sku_graph.add_edges_from(edges)

    @staticmethod
    def replace_size(name):
        name = services.clean_name(name)
        try:
            digits, unit, match = size_finder.get_digits_unit_size(
                services.clean_for_sizing(name)
            )
            name = name.replace(match, str(digits) + " " + unit)
        except SizingException:
            pass

        return name

    @staticmethod
    def tokenize(s):
        stopwords = {"ml", "gr", "adet", "ve", "and"}
        try:
            tokens = set(t for t in s.split() if len(t) > 2 and t not in stopwords)
            return tokens
        except AttributeError as e:
            logging.error(e)
            return set()

    def match_singles(self, id, name):
        tokenset = self.tokenize(name)
        candidates = [self.inverted_index.get(token, []) for token in tokenset]
        candidates = set(itertools.chain(*candidates))
        if not candidates:
            return
        for id_group in candidates:
            group_common = self.common_tokens.get(id_group, set())
            if not group_common:
                continue
            if tokenset.issuperset(group_common):
                group_all = self.group_tokens.get(id_group, set())
                if group_all.issuperset(tokenset):
                    # connect single name to a group
                    self.sku_graph.add_edges_from((id, id_group[0]))
                    self.connected_ids.add(id)
                    return name, self.group_names.get(id_group)

    def set_match(self, id_doc_pairs):
        id_groups = self.create_connected_component_groups(self.sku_graph)
        # filter single items
        id_groups = [
            id_group
            for id_group in id_groups
            if all(id in self.connected_ids for id in id_group)
        ]

        common_tokens = dict()
        group_tokens = dict()
        self.inverted_index = collections.defaultdict(set)
        self.group_names = dict()

        for id_group in tqdm(id_groups):
            names = [
                id_doc_pairs.get(id).get("clean_name")
                for id in id_group
                if "clone" not in id
            ]
            names = [n for n in names if n]
            self.group_names[tuple(id_group)] = names
            token_sets = [self.tokenize(name) for name in names]
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

        unmatched_ids = set(id_doc_pairs.keys()).difference(self.connected_ids)
        single_names = (
            (id, id_doc_pairs.get(id).get("clean_name"))
            for id in unmatched_ids
            if "clone" not in id
        )
        logging.info("matching singles..")
        matches = (
            self.match_singles(id, name) for id, name in tqdm(single_names) if name
        )
        matches = (m for m in matches if m)
        services.save_json("matches.json", list(matches))

    def exact_name_match(self, id_doc_pairs):
        name_barcode_pairs = collections.defaultdict(list)
        name_id_pairs = collections.defaultdict(list)
        for doc_id, doc in id_doc_pairs.items():
            name = doc.get("clean_name")
            sorted_name = " ".join(sorted(name.split()))
            barcodes = doc.get(keys.BARCODES, [])
            name_barcode_pairs[sorted_name] += barcodes
            name_id_pairs[sorted_name] += doc_id

        print("adding_edges_from_exact_name_match..")
        for name, barcodes in name_barcode_pairs.items():
            barcodes = set(services.flatten(barcodes))
            if len(barcodes) <= 1:
                doc_ids = name_id_pairs.get(name)
                edges = itertools.combinations(doc_ids, 2)
                self.sku_graph.add_edges_from(edges)
                self.connected_ids.update(doc_ids)

    def create_graph(self, id_doc_pairs: dict) -> nx.Graph:
        self._init_sku_graph(id_doc_pairs)
        self.barcode_match(id_doc_pairs)
        self.set_match(id_doc_pairs)
        self.exact_name_match(id_doc_pairs)
        self.promoted_match(id_doc_pairs)

        return self.sku_graph


# singleton
sku_graph_creator = SKUGraphCreator()
