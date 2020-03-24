from abc import ABC, abstractmethod
from itertools import combinations
from typing import Iterator

import networkx as nx


class GenericGraphInterface(ABC):
    def __init__(self):
        pass

    @staticmethod
    @abstractmethod
    def create_connected_component_groups(g: nx.Graph) -> list:
        pass

    @staticmethod
    @abstractmethod
    def create_graph_from_neighbor_pairs(neighbors: list):
        pass


class GenericGraph(GenericGraphInterface):
    @staticmethod
    def create_connected_component_groups(g: nx.Graph) -> list:
        return [list(group) for group in nx.connected_components(g)]

    @staticmethod
    def create_graph_from_neighbor_pairs(neighbors: Iterator):
        graph = nx.Graph()
        for neighbor_ids in neighbors:
            for node in neighbor_ids:
                graph.add_node(node)
            edges = combinations(neighbor_ids, 2)
            graph.add_edges_from(edges)
        return graph
