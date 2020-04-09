import itertools
from abc import ABC, abstractmethod

import networkx as nx

import constants as keys
from services import GenericGraph
from supermatch.matcher.barcode_matcher import BarcodeMatcher
from supermatch.matcher.exact_name_matcher import ExactNameMatcher
from supermatch.matcher.promoted_link_matcher import PromotedLinkMatcher


class AbstractSKUGraphCreator(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def _init_sku_graph(self, id_doc_pairs: dict):
        pass

    @abstractmethod
    def _add_edges_from_barcodes(self, barcode_id_pairs: dict):
        pass

    @abstractmethod
    def _add_edges_from_promoted_links(self, id_doc_pairs: dict):
        pass

    @abstractmethod
    def _add_edges_from_exact_name_match(self, exact_match_groups: list):
        pass

    @abstractmethod
    def create_graph(
            self, id_doc_pairs: dict
    ) -> nx.Graph:
        pass


class SKUGraphCreator(AbstractSKUGraphCreator, GenericGraph):
    """ Create a graph with items as vertices and barcodes as edges """

    def __init__(self):
        super().__init__()
        self.sku_graph = nx.Graph()

    def _init_sku_graph(self, id_doc_pairs):
        # add all items as nodes
        print("creating sku graph..")
        for doc_id, doc in id_doc_pairs.items():
            self.sku_graph.add_node(doc_id)

    def _add_edges_from_barcodes(self, barcode_id_pairs: dict):
        print("adding_edges_from_barcodes..")
        for barcodes, ids in barcode_id_pairs.items():
            edges = itertools.combinations(ids, 2)
            self.sku_graph.add_edges_from(edges)

    def get_digits_list_of_referenced_docs(self, id_doc_pairs, referenced_ids):
        ref_digits = [
            id_doc_pairs.get(ref_id, {}).get(keys.DIGITS) for ref_id in referenced_ids
        ]
        ref_digits = [s for s in ref_digits if s]
        ref_digits = [
            str(int(s)) if float(s).is_integer() else str(round(s, 2))
            for s in ref_digits
        ]
        return ref_digits

    def check_size_consistency(self, id_doc_pairs, filtered_referenced_ids):
        ref_digits = self.get_digits_list_of_referenced_docs(
            id_doc_pairs, filtered_referenced_ids
        )
        # max 3 sizes enforced in an sku
        return len(set(ref_digits)) <= 3

    def _add_edges_from_promoted_links(self, id_doc_pairs):
        print("addding_edges_from_promoted_links..")

        link_id_pairs = PromotedLinkMatcher.create_link_id_pairs(id_doc_pairs)

        promoted_connections = dict()
        refers_to_multiple_barcodes = set()

        for doc_id, doc in id_doc_pairs.items():
            promoted = doc.get(keys.PROMOTED, {})
            if not promoted:
                continue
            promoted_links = PromotedLinkMatcher.get_promoted_links(promoted)
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
            if id not in refers_to_multiple_barcodes
        }
        matched_using_promoted = set(promoted_connections.keys())

        for id, doc_id in promoted_connections.items():
            self.sku_graph.add_edge(id, doc_id)

        return matched_using_promoted

    def _add_edges_from_exact_name_match(self, exact_match_groups: list):
        print("adding_edges_from_exact_name_match..")
        for ids in exact_match_groups:
            edges = itertools.combinations(ids, 2)
            self.sku_graph.add_edges_from(edges)

    def create_graph(
            self, id_doc_pairs: dict
    ) -> nx.Graph:

        self._init_sku_graph(id_doc_pairs)
        matched = set()
        barcode_id_pairs = BarcodeMatcher.create_barcode_id_pairs(id_doc_pairs)
        print(len(barcode_id_pairs), "barcodes in the pool")
        self._add_edges_from_barcodes(barcode_id_pairs)

        matched_using_promoted = self._add_edges_from_promoted_links(id_doc_pairs)
        matched.update(matched_using_promoted)

        exact_match_groups = ExactNameMatcher.get_exact_match_groups(id_doc_pairs, matched)
        self._add_edges_from_exact_name_match(exact_match_groups)

        return self.sku_graph


sku_graph_creator = SKUGraphCreator()
