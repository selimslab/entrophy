from dataclasses import dataclass
from typing import Union


@dataclass
class BasicSKU:
    doc_ids: list
    sku_id: str
    product_id: str
    objectID: str

    name: str
    src: str

    prices: dict
    markets: list
    market_count: int
    best_price: Union[int, float]

    out_of_stock: bool = None

    digits: Union[int, float] = None
    unit: str = None
    size: str = None
    unit_price: Union[int, float] = None

    video_url: str = None
    tags: str = None

    barcodes: list = None


@dataclass
class SKU(BasicSKU):
    product_ids_count: dict = None
    sku_ids_count: dict = None
    docs: list = None
    links: list = None
    most_common_tokens: list = None
    variants: list = None
