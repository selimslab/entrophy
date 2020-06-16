import logging
from typing import List

import services
import constants as keys
import paths as paths

from preprocess import filter_docs, group_products
from original_to_clean import get_brand_original_to_clean, get_subcat_original_to_clean
from branding import get_brand_pool, add_brand
from subcats import get_possible_subcats_by_brand, cat_to_subcats, add_subcat
from enricher.test.inspect_results import inspect_results


def add_raw_subcats(products: List[dict]):
    # derive_subcats_from_product_cats
    for product in products:
        cats = product.get(keys.CATEGORIES, [])
        subcat_lists = [cat_to_subcats(cat) for cat in cats]
        product[keys.SUB_CATEGORIES] = services.flatten(subcat_lists)
    return products


def add_brand_and_subcat(products: List[dict]):
    """
    run the data enrichment from scratch

    next: use sku_ids, will be needed to use with supermatch
    with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
        products = pool.map(add_raw_sub_categories, tqdm(products))

    """
    # Dr O'etker : dr oetker
    brand_original_to_clean: dict = get_brand_original_to_clean(products)
    services.save_json("out/brand_original_to_clean.json", brand_original_to_clean)

    subcat_original_to_clean: dict = get_subcat_original_to_clean(products)
    services.save_json("out/subcat_original_to_clean.json", subcat_original_to_clean)

    possible_subcats_by_brand: dict = get_possible_subcats_by_brand(
        products, brand_original_to_clean, subcat_original_to_clean
    )

    brand_pool = get_brand_pool(products, possible_subcats_by_brand)
    services.save_json(paths.brand_pool, sorted(list(brand_pool)))

    logging.info("adding brand..")
    products = add_brand(products, brand_original_to_clean, brand_pool)

    logging.info("adding subcat..")
    products = add_subcat(products, subcat_original_to_clean, possible_subcats_by_brand)

    return products


def enrich_product_data(skus: dict):
    filtered_skus = filter_docs(list(skus.values()))
    products = group_products(filtered_skus)
    products = add_raw_subcats(products)
    products_with_brand_and_subcat = add_brand_and_subcat(products)
    services.save_json(
        paths.products_with_brand_and_subcat, products_with_brand_and_subcat
    )

    inspect_results(products_with_brand_and_subcat)
    print("done!")


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)
    skus: dict = services.read_json(paths.skus)
    enrich_product_data(skus)
