from abc import ABC, abstractmethod
from networkx import nx


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
    def create_graph(self, id_doc_pairs: dict) -> nx.Graph:
        pass
