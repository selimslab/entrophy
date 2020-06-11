import logging
from typing import List

import services
import constants as keys
from paths import skus_path

from preprocess import filter_docs, group_products
from original_to_clean import get_brand_original_to_clean, get_subcat_original_to_clean
from branding import get_brand_pool, add_brand
from subcats import (
    get_possible_subcats_by_brand,
    cat_to_subcats,
    add_subcat
)


def enrich_product_data(products: List[dict]):
    """
    run the data enrichment from scratch

    next: use sku_ids, will be needed to use with supermatch
    with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
        products = pool.map(add_raw_sub_categories, tqdm(products))

    """

    # derive_subcats_from_product_cats
    for product in products:
        cats = product.get(keys.CATEGORIES, [])
        subcat_lists = [cat_to_subcats(cat) for cat in cats]
        product[keys.SUB_CATEGORIES] = services.flatten(subcat_lists)

    # Dr O'etker -> dr oetker
    brand_original_to_clean: dict = get_brand_original_to_clean(products)
    subcat_original_to_clean: dict = get_subcat_original_to_clean(products)
    possible_subcats_by_brand: dict = get_possible_subcats_by_brand(
        products, brand_original_to_clean, subcat_original_to_clean
    )

    brand_pool = get_brand_pool(products, possible_subcats_by_brand)
    # services.save_json(output_dir / "brand_pool.json", sorted(list(brand_pool)))
    products = add_brand(products, brand_original_to_clean, brand_pool)

    products = add_subcat(products, subcat_original_to_clean, possible_subcats_by_brand)


def prepare_input():
    skus: list = services.read_json(skus_path).values()
    filtered_skus = filter_docs(skus)
    products = group_products(filtered_skus)
    return products


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)
    products = prepare_input()
    enrich_product_data(products)
    print("done!")
