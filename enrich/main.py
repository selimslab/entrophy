from collections import defaultdict
import logging

from typing import List

import services
import constants as keys
from paths import input_dir, output_dir

from create_product_groups import create_product_groups
from cleaner import get_clean_products
from indexer import create_indexes
from brand import add_brand_to_skus
from subcat import add_sub_cat_to_skus
from inspect_results import inspect_results


def get_sku_summary(skus_with_brand_and_sub_cat: List[dict]) -> List[dict]:
    summary_keys = {keys.CLEAN_NAMES, keys.BRAND, keys.SUB_BRAND, keys.SUBCAT}
    summary = [
        services.filter_keys(doc, summary_keys) for doc in skus_with_brand_and_sub_cat
    ]
    for doc in summary:
        doc["names"] = list(set(doc.pop(keys.CLEAN_NAMES)))[:3]

    summary = [services.remove_null_dict_values(doc) for doc in summary]
    return summary


def create_subcat_index():
    brand_subcats_pairs = services.read_json(brand_subcats_pairs_path)

    subcat_index = defaultdict(dict)
    stopwords = {"ml", "gr", "adet", "ve", "and", "ile"}

    for brand, subcats in brand_subcats_pairs.items():
        subcat_index[brand] = services.create_inverted_index(set(subcats), stopwords)

    services.save_json(output_dir / "subcat_index.json", subcat_index)


def add_brand_and_subcat(clean_products: List[dict]):
    """
    brand and subcats are together because a brand restricts the possible subcats

    1. clean and index brands + cats
        brand_subcats_pairs,
        clean_brand_original_brand_pairs,
        sub_cat_market_pairs,
    2. select a brand
        skus_with_brands
    3. select a category by restricting possible cats for this brand and prioritizing markets
        skus_with_brand_and_sub_cat
    """
    (
        brand_subcats_pairs,
        sub_cat_market_pairs,
        brand_freq,
        subcat_freq,
    ) = create_indexes()
    services.save_json(brand_subcats_pairs_path, brand_subcats_pairs)

    # add brand
    skus_with_brands = add_brand_to_skus(
        clean_products, brand_subcats_pairs, brand_freq
    )

    # add subcat
    skus_with_brand_and_sub_cat = add_sub_cat_to_skus(
        skus_with_brands, brand_subcats_pairs, sub_cat_market_pairs, subcat_freq
    )

    return skus_with_brand_and_sub_cat


def refresh():
    """
    run the data enrichment from scratch

    next: use sku_ids, will be needed to use with supermatch
    """
    skus = services.read_json(input_dir / "skus.json")
    products = create_product_groups(skus)
    clean_products = get_clean_products(products)
    products_with_brand_and_sub_cat = add_brand_and_subcat(clean_products)
    services.save_json(
        output_dir / "products_with_brand_and_sub_cat.json",
        products_with_brand_and_sub_cat,
    )

    products_with_brand_and_sub_cat_summary = get_sku_summary(
        products_with_brand_and_sub_cat
    )
    services.save_json(
        output_dir / "products_with_brand_and_sub_cat_summary.json",
        products_with_brand_and_sub_cat_summary,
    )

    inspect_results(products_with_brand_and_sub_cat_summary)
    print("done!")


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)
    brand_subcats_pairs_path = output_dir / "brand_subcats_pairs.json"
    refresh()
