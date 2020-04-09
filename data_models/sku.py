from dataclasses import dataclass
from typing import Union


@dataclass
class SKU:
    objectID: str = None
    docs: list = None
    doc_ids: list = None
    sku_id: str = None
    product_id: str = None
    product_ids_count: dict = None
    sku_ids_count: dict = None
    links: list = None
    name: str = None
    src: str = None
    prices: dict = None
    market: str = None
    out_of_stock: bool = None
    digits: Union[int, float] = None
    unit: str = None
    size: str = None
    unit_price: Union[int, float] = None
    best_price: Union[int, float] = None
    markets: list = None
    market_count: int = None
    video_url: str = None
    tags: str = None
    most_common_tokens: list = None
    barcodes: list = None
    options: list = None
