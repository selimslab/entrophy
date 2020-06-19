from collections import Counter
import logging
from typing import List

from tqdm import tqdm

import services
import constants as keys

from freq import get_brand_freq


def search_vendor_given_brands(product, clean_brands):
    brands_in_name = []
    clean_names = product.get(keys.CLEAN_NAMES, [])
    for brand in services.sorted_counter(clean_brands):
        for name in clean_names:
            # brand is in first 4 tokens mostly
            beginning_of_name = " ".join(name.split()[:4])
            if brand in beginning_of_name:
                brands_in_name.append(brand)
    return brands_in_name


def select_most_frequent_brand(brand_candidates: list, brand_freq: dict) -> str:
    """ return the_most_frequent_brand"""
    brand_candidates_with_freq = {
        brand: brand_freq.get(brand, 0) for brand in set(brand_candidates)
    }
    the_most_frequent_brand = services.get_most_frequent_key(brand_candidates_with_freq)
    return the_most_frequent_brand


def global_brand_search(clean_names, brand_pool):
    # no vendor given brand, search global pool
    # to_partial_search = set()
    brands_in_name = []
    for name in clean_names:
        # a b c -> a, a b, a b c
        start_strings = services.string_to_extending_windows(name, end=3)
        for s in start_strings:
            if s in brand_pool:
                brands_in_name.append(s)

    return brands_in_name


def check_root_brand(brand_freq, selected):
    current_freq = brand_freq.get(selected, 0)
    possible_roots = services.string_to_extending_windows(selected)
    possible_roots.sort(key=len)
    for root in possible_roots:
        if brand_freq.get(root, 0) > current_freq:
            selected = root
            current_freq = brand_freq.get(root)
    return selected


def add_brand(
        products: List[dict], brand_original_to_clean: dict, brand_pool: set
) -> List[dict]:
    """

    """
    logging.info("adding brand..")

    brand_freq: dict = get_brand_freq(products, brand_original_to_clean)
    services.save_json("out/brand_freq.json", services.sorted_counter(brand_freq))

    # brand_pool_sorted = services.sort_from_long_to_short(brand_pool)
    for product in tqdm(products):
        clean_names = product.get(keys.CLEAN_NAMES, [])
        vendor_given_brands = product.get(keys.BRANDS_MULTIPLE)
        clean_brands = [brand_original_to_clean.get(b) for b in vendor_given_brands]
        product[keys.CLEAN_BRANDS] = clean_brands

        brands_in_name = search_vendor_given_brands(product, clean_brands)

        if brands_in_name:
            selected = brands_in_name[0]

            if len(selected.split()) > 1:
                selected = check_root_brand(brand_freq, selected)

            product[keys.BRAND] = selected
        else:
            global_brands = global_brand_search(clean_names, brand_pool)
            if global_brands:
                selected = select_most_frequent_brand(global_brands, brand_freq)

                if len(selected.split()) > 1:
                    selected = check_root_brand(brand_freq, selected)

                product[keys.BRAND] = selected

        # TODO partial brand match

    return products


def get_brand_pool(products: List[dict], possible_subcats_by_brand: dict) -> set:
    # brands given by vendors
    brands = possible_subcats_by_brand.keys()
    brand_pool = set(brands)

    window_frequencies = Counter()
    max_brand_size = 3
    for product in products:
        clean_names = product.get(keys.CLEAN_NAMES, [])
        for name in clean_names:
            sliding_windows = services.string_to_extending_windows(name, max_brand_size)
            window_frequencies.update(sliding_windows)

    services.save_json(
        "out/window_frequencies.json",
        services.sorted_counter(window_frequencies),
    )

    most_frequent_start_strings = {
        s: count for s, count in window_frequencies.items() if count > 10
    }

    # OrderedDict(Counter(groups).most_common())
    brand_pool.update(set(most_frequent_start_strings.keys()))

    to_filter_out = {"brn ", "markasiz", "erkek", "kadin", " adet"}
    brand_pool = {
        services.remove_whitespace(b)
        for b in brand_pool
        if (len(b) > 2 and not any(bad in b for bad in to_filter_out))
    }
    return brand_pool


def check_partial(brand_pool_sorted, to_partial_search):
    """ l paris -> loreal paris ? """
    brand_candidates = set()
    for brand in brand_pool_sorted:
        if brand in brand_candidates:
            continue
        for s in to_partial_search:
            if brand in brand_candidates:
                continue
            if services.partial_string_search(s, brand):
                brand_candidates.add(s)
    return brand_candidates
