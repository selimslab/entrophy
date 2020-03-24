from dataclasses import dataclass
from typing import Union


@dataclass
class Product:
    links: list = None
    name: str = None
    src: str = None
    price: Union[int, float] = None
    markets: list = None
    market_count: int = None
    variants: list = None
    tags: list = None
    objectID: str = None
    barcodes: list = None
