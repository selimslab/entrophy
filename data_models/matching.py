from dataclasses import dataclass


@dataclass
class MatchingCollection:
    skus: list
    products: list
    id_tree: dict


@dataclass
class MatchingMechanism:
    barcode: bool
    promoted: bool
    exact_name: bool
