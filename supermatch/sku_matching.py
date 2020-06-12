import itertools
import networkx as nx
from tqdm import tqdm
import logging
import collections

import constants as keys
import services
from .test_set_match import test_set_match
from .promoted import promoted_match
from .set_match import set_match


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

    def exact_name_match(self):
        """ merge barcode-less items with the same name
        TODO iff they have the same size
        """
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

        print("name_barcode_pairs", len(name_barcode_pairs))

        for name, barcodes in name_barcode_pairs.items():
            if len(barcodes) <= 1:
                doc_ids = name_id_pairs.get(name)
                single_doc_ids = [id for id in doc_ids if id not in self.connected_ids]
                if len(single_doc_ids) > 1:
                    edges = itertools.combinations(single_doc_ids, 2)
                    self.sku_graph.add_edges_from(edges)
                    self.stages.update({**dict.fromkeys(single_doc_ids, "exact_name")})
                    self.connected_ids.update(single_doc_ids)

    def create_graph(self):
        self.init_sku_graph()

        print("barcode match..")
        self.barcode_match()

        print("exact_name_match..")
        self.exact_name_match()

        print("set match..")
        set_match(self)

        print("promoted match..")
        promoted_match(self)

        return self.sku_graph, self.stages
