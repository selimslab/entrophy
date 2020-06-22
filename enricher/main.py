import logging
from typing import List

import services
import constants as keys
import paths as paths

from preprocess import filter_docs, group_products
from original_to_clean import (
    get_brand_original_to_clean,
    get_subcat_original_to_clean,
    get_color_original_to_clean,
)
from branding import get_brand_pool, add_brand
from subcats import get_possible_subcats_by_brand, add_raw_subcats, add_subcat
from inspect_results import inspect_results
from filter_names import add_filtered_names
from sub_brand import get_filtered_names_tree, create_possible_sub_brands
from analysis import analyze_subcat, analyze_brand


def add_brand_and_subcat(products: List[dict]):
    """
    run the data enrichment from scratch

    next: use sku_ids, will be needed to use with supermatch
    with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
        products = pool.map(add_raw_sub_categories, tqdm(products))

    """
    # Dr O'etker : dr oetker
    brand_original_to_clean: dict = get_brand_original_to_clean(products)
    services.save_json(paths.brand_original_to_clean, brand_original_to_clean)

    subcat_original_to_clean: dict = get_subcat_original_to_clean(products)
    services.save_json(paths.subcat_original_to_clean, subcat_original_to_clean)

    possible_subcats_by_brand: dict = get_possible_subcats_by_brand(
        products, brand_original_to_clean, subcat_original_to_clean
    )
    services.save_json(
        paths.output_dir / "possible_subcats_by_brand.json", possible_subcats_by_brand
    )

    brand_pool: set = get_brand_pool(products, possible_subcats_by_brand)
    services.save_json(paths.brand_pool, sorted(list(brand_pool)))

    products = add_brand(products, brand_original_to_clean, brand_pool)

    products = add_subcat(products, subcat_original_to_clean)

    return products


def select_color(clean_names, clean_colors):
    for name in clean_names:
        for color in clean_colors:
            if color in name:
                return color


def add_color(products):
    color_original_to_clean = get_color_original_to_clean(products)
    services.save_json(paths.color_original_to_clean, color_original_to_clean)

    for product in products:
        clean_names = product.get(keys.CLEAN_NAMES, [])
        colors = product.get(keys.COLOR, []) + product.get(keys.VARIANT_NAME, [])
        clean_colors = [color_original_to_clean.get(color) for color in colors]
        clean_colors = [c for c in clean_colors if c]
        product[keys.CLEAN_COLORS] = clean_colors
        color = select_color(clean_names, clean_colors)
        if color:
            product[keys.SELECTED_COLOR] = color

    return products


def enrich_product_data(skus: dict):
    skus = filter_docs(list(skus.values()))

    logging.info("add_raw_subcats..")
    skus = add_raw_subcats(skus)

    logging.info("group_products..")
    products = group_products(skus)

    logging.info("add_color..")
    products = add_color(products)

    products = add_brand_and_subcat(products)

    # for sub brand
    products = add_filtered_names(products)

    services.save_json(paths.products_out, products)

    filtered_names_tree = get_filtered_names_tree(products)
    services.save_json(paths.filtered_names_tree, filtered_names_tree)

    inspect_results(products)

    create_possible_sub_brands(filtered_names_tree)

    analyze_brand()
    analyze_subcat()

    print("done!")


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)
    skus: dict = services.read_json(paths.skus)
    enrich_product_data(skus)
