import re
from typing import List, Dict, Union, Iterator
from collections import defaultdict
import logging
from tqdm import tqdm

import services
import constants as keys

from freq import get_subcat_freq


def add_subcat(products: List[dict],
               subcat_original_to_clean: Dict[str, str],
               possible_subcats_by_brand: Dict[str, set]):
    subcat_freq: dict = get_subcat_freq(products, subcat_original_to_clean)
    for product in products:
        possible_subcats_for_this_product: list = get_possible_subcats_for_this_product(
            product, possible_subcats_by_brand, subcat_original_to_clean
        )
        subcat_candidates: list = get_subcat_candidates(
            product, possible_subcats_for_this_product
        )
        if subcat_candidates:
            product[keys.SUBCAT_CANDIDATES] = dict(Counter(subcat_candidates))
            product[keys.SUBCAT] = select_subcat(subcat_candidates, subcat_freq)
    return products


def cat_to_subcats(cat: Union[list, str]) -> List[str]:
    if isinstance(cat, list):
        cat = cat[-1]
    # "Şeker, Tuz & Baharat / un " ->  [Şeker, Tuz, Baharat, un]
    subcat = re.split("/ |, |&", cat)
    return subcat


def test_cat_to_subcats():
    ...


def select_subcat(subcat_candidates: Iterator, subcat_freq: dict):
    if subcat_candidates:
        subcat_candidates_with_freq = {
            sub: subcat_freq.get(sub, 0) for sub in subcat_candidates
        }
        the_most_frequent_subcat = services.get_most_frequent_key(subcat_candidates_with_freq)
        return the_most_frequent_subcat


def get_possible_subcats_by_brand(
        products, brand_original_to_clean, subcat_original_to_clean
) -> dict:
    """ which subcats are possible for this brand

    "ariel": [
        "sivi jel deterjan",
        "camasir yikama urunleri",
        ...
    ]
    """
    possible_subcats_by_brand = defaultdict(set)

    for product in products:
        brands = product.get(keys.BRANDS_MULTIPLE, [])
        subcats = product.get(keys.SUB_CATEGORIES, [])

        clean_brands = (brand_original_to_clean.get(b) for b in brands)
        clean_subcats = (subcat_original_to_clean.get(s) for s in subcats)

        for clean_brand in clean_brands:
            possible_subcats_by_brand[clean_brand].add(set(clean_subcats))

    return possible_subcats_by_brand


def get_possible_subcats_for_this_product(
        product: dict, possible_subcats_by_brand: dict, subcat_original_to_clean: dict
) -> list:
    brand_candidates = product.get(keys.BRAND_CANDIDATES)
    possible_subcats = [
        possible_subcats_by_brand.get(brand, []) for brand in brand_candidates
    ]

    brand = product.get(keys.BRAND)
    # possible_subcats will be a union of possible_subcats for all start combinations
    # ["loreal", "loreal excellence", "loreal excellence intense"]
    if brand:
        brand_tokens = brand.split()
        for i in range(1, len(brand_tokens) + 1):
            possible_parent_brand = " ".join(brand_tokens[0:i])
            possible_subcats += possible_subcats_by_brand.get(possible_parent_brand, [])

    clean_subcats = [
        subcat_original_to_clean.get(sub)
        for sub in product.get(keys.SUB_CATEGORIES, [])
    ]
    possible_subcats += clean_subcats

    possible_subcats = list(set(services.flatten(possible_subcats)))

    return possible_subcats


def get_subcat_candidates(product: dict, possible_subcats_for_this_product: list) -> list:
    clean_names = product.get(keys.CLEAN_NAMES, [])

    sub_cat_candidates = []
    for sub in possible_subcats_for_this_product:
        for name in clean_names:
            if sub in name or services.partial_string_search(name, sub):
                sub_cat_candidates.append(sub)
    return sub_cat_candidates


def filter_sub_cat_candidates(sub_cat_candidates, brand_pool):
    # dedup, remove very long sub_cats, they are mostly wrong, remove if it's also a brand
    return list(
        set(
            s
            for s in sub_cat_candidates
            if s and 1 < len(s) < 30 and "indirim" not in s and s not in brand_pool
        )
    )

