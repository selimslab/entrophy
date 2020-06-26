from collections import Counter
import logging
from typing import List

from tqdm import tqdm

import services
import constants as keys

from prep.freq import get_brand_freq


def search_vendor_given_brands(clean_names, clean_brands):
    brands_in_name = []
    for brand in services.sorted_counter(clean_brands):
        for name in clean_names:
            # brand is in first 4 tokens mostly
            beginning_of_name = " ".join(name.split()[:4])
            if brand in beginning_of_name:
                brands_in_name.append(brand)
    return brands_in_name


def check_root_brand(brand_freq, brand):
    current_freq = brand_freq.get(brand, 0)
    possible_roots = services.string_to_extending_windows(brand)
    possible_roots.sort(key=len)
    selected = brand
    for root in possible_roots:
        root_freq = brand_freq.get(root, 0)
        if root_freq > current_freq:
            selected = root
            current_freq = root_freq
    return selected


def get_brand(product):
    clean_names = product.get(keys.CLEAN_NAMES, [])
    clean_brands = product.get(keys.CLEAN_BRANDS, [])
    brands_in_name = search_vendor_given_brands(clean_names, clean_brands)
    if brands_in_name:
        return brands_in_name[0]
    elif clean_brands:
        return services.get_most_common_item(clean_brands)


def add_brand(products: List[dict]) -> List[dict]:
    logging.info("adding brand..")

    brand_freq: dict = get_brand_freq(products)

    for product in tqdm(products):
        brand = get_brand(product)
        if brand:
            if len(brand.split()) > 1:
                brand = check_root_brand(brand_freq, brand)
            product[keys.BRAND] = brand

    return products


def get_window_frequencies(products: List[dict]):
    window_frequencies = Counter()
    max_brand_size = 3
    for product in products:
        clean_names = product.get(keys.CLEAN_NAMES, [])
        for name in clean_names:
            sliding_windows = services.string_to_extending_windows(name, max_brand_size)
            window_frequencies.update(sliding_windows)

    return window_frequencies


def filter_brands(brand_pool):
    to_filter_out = {"brn ", "markasiz", "erkek", "kadin", " adet"}
    return {
        services.remove_whitespace(b)
        for b in brand_pool
        if (b and len(b) > 2 and not any(bad in b for bad in to_filter_out))
    }


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
