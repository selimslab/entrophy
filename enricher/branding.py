from collections import Counter, OrderedDict
import logging
from typing import List

from tqdm import tqdm

import services
import constants as keys
from paths import output_dir

from freq import get_brand_freq


def add_brand(
    products: List[dict], brand_original_to_clean: dict, brand_pool: set
) -> List[dict]:
    brand_freq: dict = get_brand_freq(products, brand_original_to_clean)
    brand_pool_sorted = services.sort_from_long_to_short(brand_pool)
    for product in tqdm(products):
        brand_candidates: set = get_brand_candidates(
            product, brand_pool, brand_pool_sorted
        )
        product[keys.BRAND_CANDIDATES] = list(brand_candidates)

        the_most_frequent_brand = select_brand(brand_candidates, brand_freq)
        product[keys.BRAND] = the_most_frequent_brand

    return products


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


def get_brand_pool(products: List[dict], possible_subcats_by_brand: dict) -> set:
    # brands given by vendors
    brands = possible_subcats_by_brand.keys()
    brand_pool = set(brands)

    names = [product.get(keys.CLEAN_NAMES, []) for product in products]
    most_frequent_start_strings = get_frequent_start_strings_as_brands(names)
    brand_pool.update(most_frequent_start_strings)

    to_filter_out = {"brn ", "markasiz", "erkek", "kadin"}
    brand_pool = {
        b
        for b in brand_pool
        if (len(b) > 2 and not any(bad in b for bad in to_filter_out))
    }

    return brand_pool


def get_brand_candidates(
    product: dict, brand_pool: set, brand_pool_sorted: list
) -> set:
    """
    find brand first

    there only a few possible cats for this brand
    indexes should reflect that too
    """
    brand_candidates = set()
    clean_names = product.get(keys.CLEAN_NAMES, [])

    # O(ok + (len(names)-ok)*len(brand_pool))

    # instead of searching every possible brand in name, we search parts of name in brands set
    to_partial_search = set()
    for name in clean_names:
        # brand is in first 4 tokens mostly
        start_strings = services.string_to_extending_windows(name, 4)
        for s in start_strings:
            if s in brand_pool:
                brand_candidates.add(s)
            else:
                to_partial_search.add(s)

    if not brand_candidates and to_partial_search:
        for brand in brand_pool_sorted:
            if brand in brand_candidates:
                continue
            for s in to_partial_search:
                if services.partial_string_search(s, brand):
                    brand_candidates.add(s)
                    print((s, brand))

    return brand_candidates


def select_brand(brand_candidates: set, brand_freq: dict) -> str:
    brand_candidates_with_freq = {
        brand: brand_freq.get(brand, 0) for brand in set(brand_candidates)
    }
    the_most_frequent_brand = services.get_most_frequent_key(brand_candidates_with_freq)
    return the_most_frequent_brand
