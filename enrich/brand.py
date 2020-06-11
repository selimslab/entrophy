from collections import Counter, OrderedDict
import logging
from typing import List

from tqdm import tqdm

import services
import constants as keys
from paths import output_dir


def select_brand(brand_candidates: list, brand_freq: dict) -> tuple:
    if brand_candidates:
        brand_candidates = list(set(brand_candidates))
        brand_candidates_with_freq = {
            brand: brand_freq.get(brand, 0) for brand in brand_candidates
        }
        root_brand = services.get_most_frequent_key(brand_candidates_with_freq)
        # select the longest
        sub_brand = ""
        longest_brand = sorted(brand_candidates, key=len)[-1]
        if longest_brand != root_brand:
            sub_brand = longest_brand
        return root_brand, sub_brand


def get_brand_candidates(sku: dict, brand_pool: set) -> list:
    """
    find brand first

    there only a few possible cats for this brand
    indexes should reflect that too
    """
    candidates = []
    candidates += sku.get(keys.CLEAN_BRANDS, [])

    clean_names = sku.get(keys.CLEAN_NAMES, [])

    # instead of searching every possible brand in name, we search parts of name in brands set
    for name in clean_names:
        # brand is in first 4 tokens mostly
        name_tokens = name.split()
        start_strings = [" ".join(name_tokens[:i]) for i in range(1, 4)]
        brands_from_frequent_words = [s for s in start_strings if s in brand_pool]
        candidates += brands_from_frequent_words

    return candidates


def get_frequencies_for_all_start_combinations(names: List[list]) -> dict:
    token_lists = services.get_token_lists(names)
    groups = []
    logging.info("get_frequencies_for_all_start_combinations..")
    for token_list in tqdm(token_lists):
        for i in range(1, len(token_list) + 1):
            groups.append(" ".join(token_list[0:i]))
    groups = [s for s in groups if len(s) > 2]
    freq = OrderedDict(Counter(groups).most_common())
    return freq


def get_frequent_start_strings_as_brands(names: List[list]) -> set:
    freq = get_frequencies_for_all_start_combinations(names)
    filtered_freq = {s: freq for s, freq in freq.items() if freq > 60}
    services.save_json(
        output_dir / "most_frequent_start_strings.json",
        OrderedDict(sorted(filtered_freq.items())),
    )

    max_brand_size = 2
    most_frequent_start_strings = set(filtered_freq.keys())
    most_frequent_start_strings = {
        b for b in most_frequent_start_strings if len(b.split()) <= max_brand_size
    }

    return most_frequent_start_strings


def add_brand_to_skus(
    clean_products: List[dict], brand_subcats_pairs: dict, brand_freq: dict
) -> List[dict]:
    """
    0. cat and subcat are different things, beware
    1. clean well
    2. using ty_raw, wat_raw, and full skus  ->
    create
    brand : [possible cats]
    cat : [possible brands]

    so given a brand, the possible cats will be known
    """

    # brands given by vendors
    brands = brand_subcats_pairs.keys()
    brand_pool = set(brands)

    names = [sku.get(keys.CLEAN_NAMES, []) for sku in clean_products]
    most_frequent_start_strings = get_frequent_start_strings_as_brands(names)
    brand_pool.update(most_frequent_start_strings)

    services.save_json(output_dir / "brand_pool.json", sorted(list(brand_pool)))

    bad_words = {"brn ", "markasiz", "erkek", "kadin"}

    logging.info("adding brand..")
    for sku in tqdm(clean_products):
        brand_candidates = get_brand_candidates(sku, brand_pool)
        brand_candidates = [
            b
            for b in brand_candidates
            if len(b) > 2 and not any(bad in b for bad in bad_words)
        ]

        sku[keys.BRAND_CANDIDATES] = dict(Counter(brand_candidates))
        result = select_brand(brand_candidates, brand_freq)
        if result:
            root_brand, sub_brand = result
            if root_brand:
                sku[keys.BRAND] = root_brand
            if sub_brand:
                # sku[keys.SUB_BRAND] = sub_brand
                ...

    return clean_products
