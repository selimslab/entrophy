from dataclasses import dataclass, field
from typing import Union


@dataclass
class BasicSKU:
    doc_ids: list = field(default_factory=list)
    sku_id: str = None
    product_id: str = None
    objectID: str = None

    name: str = None
    src: str = None

    prices: dict = field(default_factory=dict)
    markets: list = field(default_factory=list)
    market_count: int = None
    best_price: Union[int, float] = None

    out_of_stock: bool = None

    digits: Union[int, float] = None
    unit: str = None
    size: str = None
    unit_price: Union[int, float] = None

    video_url: str = None
    tags: str = None

    barcodes: list = field(default_factory=list)


@dataclass
class SKU(BasicSKU):
    product_ids_count: dict = None
    sku_ids_count: dict = None
    docs: list = None
    links: list = None
    most_common_tokens: list = None
    variants: list = None
