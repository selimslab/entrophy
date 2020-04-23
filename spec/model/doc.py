from dataclasses import dataclass
from typing import Union


@dataclass
class BaseDoc:
    link: str = None
    name: str = None
    brand: str = None
    src: str = None
    barcodes: list = None
    price: Union[int, float] = None
    market: str = None
    out_of_stock: bool = None
    historical_prices: list = None
    promoted: dict = None
    variants: dict = None
    variant_name: str = None
    sku_id: str = None


@dataclass
class RawDoc(BaseDoc):
    product_id: str = None
    google_info: list = None
