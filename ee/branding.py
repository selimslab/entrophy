from collections import Counter, OrderedDict
import logging
from typing import List

from tqdm import tqdm

import services
import constants as keys
from paths import output_dir


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


def get_brand_candidates(sku: dict, brand_pool: set) -> list:
    """
    find brand first

    there only a few possible cats for this brand
    indexes should reflect that too
    """
    candidates = []
    clean_names = sku.get(keys.CLEAN_NAMES, [])

    # instead of searching every possible brand in name, we search parts of name in brands set
    for name in clean_names:
        # brand is in first 4 tokens mostly
        start = " ".join(name.split()[:4])
        for brand in brand_pool:
            is_brand_in_string = services.partial_string_search(start, brand)
            if is_brand_in_string:
                candidates += brand
                if start not in brand_pool:
                    print(start, brand)

    return candidates


def select_brand(brand_candidates, brand_freq):
    brand_candidates_with_freq = {
        brand: brand_freq.get(brand, 0) for brand in set(brand_candidates)
    }
    the_most_frequent_brand = services.get_most_frequent_key(brand_candidates_with_freq)
    return the_most_frequent_brand
