import itertools
import networkx as nx
from tqdm import tqdm
import logging
import collections

import constants as keys
import services
from supermatch.docs_to_sku.promoted import promoted_match
from supermatch.docs_to_sku.set_match import set_match
from supermatch.docs_to_sku.same_names import exact_name_match


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

            for code in barcodes:
                barcode_id_pairs[code].add(doc_id)

        logging.info(f"adding_edges using {len(barcode_id_pairs)} barcodes")
        for ids in tqdm(barcode_id_pairs.values()):
            edges = itertools.combinations(ids, 2)
            self.sku_graph.add_edges_from(edges)
            self.connected_ids.update(ids)

        self.stages = {**dict.fromkeys(self.connected_ids, "barcode")}

    def create_graph(self):
        self.init_sku_graph()

        print("barcode match..")
        self.barcode_match()

        print("exact_name_match..")
        exact_name_match(self)

        print("set match..")
        set_match(self)

        print("promoted match..")
        promoted_match(self)

        return self.sku_graph, self.stages

    def single_doc_generator(self):
        unmatched_ids = set(self.id_doc_pairs.keys()).difference(self.connected_ids)
        for doc_id in unmatched_ids:
            if "clone" not in doc_id:
                doc = self.id_doc_pairs.get(doc_id, {})
                yield doc_id, doc

    def get_connected_groups(self) -> list:
        id_groups = self.create_connected_component_groups(self.sku_graph)

        # filter out single item groups
        id_groups = [
            id_group
            for id_group in id_groups
            if all(id in self.connected_ids for id in id_group)
        ]
        return id_groups
