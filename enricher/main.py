import logging
from typing import List

import services
import constants as keys
import paths as paths

from preprocess import filter_docs, group_products
from original_to_clean import get_brand_original_to_clean, get_subcat_original_to_clean
from branding import get_brand_pool, add_brand
from subcats import get_possible_subcats_by_brand, cat_to_subcats, add_subcat


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

    # Dr O'etker : dr oetker
    brand_original_to_clean: dict = get_brand_original_to_clean(products)
    subcat_original_to_clean: dict = get_subcat_original_to_clean(products)
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


def prepare_input(skus: dict):
    filtered_skus = filter_docs(list(skus.values()))
    products = group_products(filtered_skus)
    return products


def go():
    products = prepare_input(skus)
    products_with_brand_and_subcat = enrich_product_data(products)
    services.save_json(
        paths.products_with_brand_and_subcat, products_with_brand_and_subcat
    )


def is_valid_color(c: str):
    return c and not c.isdigit() and "nocolor" not in c


def color_to_clean():
    colors = services.read_json(paths.colors)

    color_original_to_clean = {
        c: services.clean_string(c) for c in colors
    }
    color_original_to_clean = {k: clean_color for k, clean_color in color_original_to_clean.items()
                               if is_valid_color(clean_color)}

    services.save_json(paths.clean_colors, color_original_to_clean)


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)
    # skus: dict = services.read_json(paths.skus)
    color_to_clean()
    print("done!")
    """
    remove sub tokens of a string, too
    
    plural for subcat only 
    
    restrict color by brand or subcat 
    """
