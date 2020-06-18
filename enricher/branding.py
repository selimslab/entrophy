from collections import Counter, OrderedDict
import logging
from typing import List

from tqdm import tqdm

import services
import constants as keys
from paths import output_dir

from freq import get_brand_freq


def select_brand(brand_candidates: set, brand_freq: dict) -> str:
    brand_candidates_with_freq = {
        brand: brand_freq.get(brand, 0) for brand in set(brand_candidates)
    }
    the_most_frequent_brand = services.get_most_frequent_key(brand_candidates_with_freq)
    return the_most_frequent_brand


def add_brand(
        products: List[dict], brand_original_to_clean: dict, brand_pool: set
) -> List[dict]:
    brand_freq: dict = get_brand_freq(products, brand_original_to_clean)
    services.save_json("out/brand_freq.json", services.sorted_counter(brand_freq))

    # brand_pool_sorted = services.sort_from_long_to_short(brand_pool)
    for product in tqdm(products):
        brands_in_name = []
        clean_names = product.get(keys.CLEAN_NAMES, [])

        vendor_given_brands = product.get(keys.BRANDS_MULTIPLE)
        if vendor_given_brands:
            # search in the names
            for name in clean_names:
                # brand is in first 4 tokens mostly
                beginning_of_name = " ".join(name.split()[:4])
                for brand in vendor_given_brands:
                    if brand in beginning_of_name:
                        brands_in_name.append(brand)
        else:
            # no vendor given brand, search global pool
            # to_partial_search = set()
            for name in clean_names:
                # a b c -> a, a b, a b c
                beginning_of_name = " ".join(name.split()[:3])
                start_strings = services.string_to_extending_windows(beginning_of_name)
                for s in start_strings:
                    if s in brand_pool:
                        brands_in_name.append(s)

        if brands_in_name:
            product[keys.BRAND_CANDIDATES] = list(brands_in_name)
            the_most_frequent_brand = select_brand(set(brands_in_name), brand_freq)
            product[keys.BRAND] = the_most_frequent_brand

    return products


def get_brand_pool(products: List[dict], possible_subcats_by_brand: dict) -> set:
    # brands given by vendors
    brands = possible_subcats_by_brand.keys()
    brand_pool = set(brands)

    window_frequencies = Counter()
    max_brand_size = 4
    for product in products:
        clean_names = product.get(keys.CLEAN_NAMES, [])
        for name in clean_names:
            sliding_windows = services.string_to_extending_windows(name, max_brand_size)
            window_frequencies.update(sliding_windows)

    most_frequent_start_strings = {
        s for s, count in window_frequencies.items() if count > 42
    }

    services.save_json("out/most_frequent_start_strings.json",
                       OrderedDict(Counter(most_frequent_start_strings).most_common()))
    # OrderedDict(Counter(groups).most_common())
    brand_pool.update(most_frequent_start_strings)

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
