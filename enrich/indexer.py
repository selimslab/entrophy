from collections import defaultdict, Counter
import logging
import os
from typing import Iterable

import services
import constants as keys

from mongo_service import get_raw_docs_with_markets_and_cats_only

from subcat import clean_sub_cats

from paths import input_dir, output_dir


def index_brands_and_subcats() -> tuple:
    """

    "finish": [
        "kirec onleyici",
        "bulasik yikama urunleri",
        ...
        ]

    next: add brand_freq to choose root brand

    """

    brand_subcats_pairs = defaultdict(set)
    clean_brand_original_brand_pairs = {}
    sub_cat_market_pairs = defaultdict(set)
    brand_freq = Counter()  # how many items has been given this  brand by a vendor
    subcat_freq = Counter()

    def update_brand_subcats_pairs(brands: Iterable, subcats: Iterable, market):
        brands = list(set(brands))
        subcats = list(set(subcats))

        clean_to_original = {services.clean_name(b): b for b in brands}
        clean_brand_original_brand_pairs.update(clean_to_original)
        clean_brands = [
            b for b in clean_to_original.keys() if len(b) > 1 and "brn " not in b
        ]
        brand_freq.update(clean_brands)

        brandset = set(clean_brands)

        clean_subcats = services.clean_list_of_strings(subcats)
        clean_subcats = [sub for sub in clean_subcats if sub]
        subcat_freq.update(clean_subcats)

        for sub in clean_subcats:
            sub_cat_market_pairs[sub].add(market)

        for b in brandset:
            brand_subcats_pairs[b].update(clean_subcats)

    def add_from_raw_docs():
        raw_docs_path = input_dir / "raw_docs.json"
        if not os.path.exists(raw_docs_path):
            cursor = get_raw_docs_with_markets_and_cats_only()
            raw_docs = list(cursor)
            services.save_json(raw_docs_path, raw_docs)
        else:
            raw_docs = services.read_json(raw_docs_path)

        for doc in raw_docs:
            brand = doc.get(keys.BRAND)
            cats = doc.get(keys.CATEGORIES, [])
            market = doc.get(keys.MARKET)

            brands = [brand]
            subcats = clean_sub_cats(cats)
            update_brand_subcats_pairs(brands, subcats, market)

    logging.info("creating brand_subcats_pairs..")
    add_from_raw_docs()

    return (
        brand_subcats_pairs,
        clean_brand_original_brand_pairs,
        sub_cat_market_pairs,
        brand_freq,
        subcat_freq,
    )


def create_indexes():
    (
        brand_subcats_pairs,
        clean_brand_original_brand_pairs,
        sub_cat_market_pairs,
        brand_freq,
        subcat_freq,
    ) = index_brands_and_subcats()

    subcat_freq = {
        s: count for s, count in subcat_freq.items() if len(s) >= 2 and count >= 2
    }
    services.save_json(output_dir / "brand_freq.json", brand_freq)

    sub_cat_market_pairs = services.convert_dict_set_values_to_list(
        sub_cat_market_pairs
    )
    services.save_json(output_dir / "sub_cat_market_pairs.json", sub_cat_market_pairs)

    brand_subcats_pairs = services.convert_dict_set_values_to_list(brand_subcats_pairs)
    services.save_json(
        output_dir / "clean_brand_original_brand_pairs.json",
        clean_brand_original_brand_pairs,
    )

    return brand_subcats_pairs, sub_cat_market_pairs, brand_freq, subcat_freq
