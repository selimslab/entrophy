from dataclasses import dataclass
from typing import Callable


@dataclass
class SpiderConfig:
    name: str
    base_domain: str

    category_function: Callable
    extract_function: Callable

    table_selector: str
    product_selector: str

    next_page_href: str

    is_basic: bool
