import re
import itertools
from typing import List, Dict, Union, Iterator
from collections import Counter
import logging
from tqdm import tqdm

import services
import constants as keys


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


def get_possible_subcats_for_this_product(
        product, possible_subcats_by_brand, subcat_original_to_clean
):
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


def get_subcat_candidates(product, possible_subcats_for_this_product):
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


def add_sub_cat_to_skus(
        skus: List[dict], brand_subcats_pairs: Dict[str, list], subcat_freq: dict,
) -> List[dict]:
    """
    There are a set of possible subcats for a given brand

    we check them if any of them is in any of the names of the given sku
    this leaves us with a few candidates

    then we choose prioritizing by market
    """
    logging.info("adding subcat..")
    for sku in tqdm(skus):
        sub_cat_candidates = []

        clean_names = sku.get(keys.CLEAN_NAMES, [])

        brand = sku.get(keys.BRAND)

        # for example,
        # for brand loreal excellence intense
        # possible_subcats will be a union of possible_subcats for all start combinations
        # ["loreal", "loreal excellence", "loreal excellence intense"]
        possible_subcats_for_this_brand = []
        if brand:
            brand_tokens = brand.split()
            for i in range(1, len(brand_tokens) + 1):
                possible_parent_brand = " ".join(brand_tokens[0:i])
                possible_subcats_for_this_brand += brand_subcats_pairs.get(
                    possible_parent_brand, []
                )

    return skus
