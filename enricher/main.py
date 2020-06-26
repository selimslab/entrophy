import logging
import services
import constants as keys
import paths as paths

from prep.grouper import filter_docs, group_products
from cleaners.brand_to_clean import get_brand_original_to_clean
from cleaners.subcat_to_clean import get_subcat_original_to_clean
from cleaners.color_to_clean import get_color_original_to_clean

from selectors.brand_selector import get_brand_pool, add_brand
from prep.cat_to_subcat import add_raw_subcats
from selectors.subcat_selector import get_possible_subcats_by_brand, add_subcat
from inspect_results import inspect_results
from prep.filter_names import add_filtered_names
from selectors.sub_brand_selector import (
    get_filtered_names_tree,
    create_possible_sub_brands,
    select_subbrand,
)
from analysis import analyze_subcat, analyze_brand


def get_indexes(products):
    brand_original_to_clean: dict = get_brand_original_to_clean(products)

    clean_brands = set(brand_original_to_clean.values())
    subcat_original_to_clean: dict = get_subcat_original_to_clean(
        products, clean_brands
    )

    possible_subcats_by_brand: dict = get_possible_subcats_by_brand(
        products, brand_original_to_clean, subcat_original_to_clean
    )

    services.save_json(paths.brand_original_to_clean, brand_original_to_clean)
    services.save_json(paths.subcat_original_to_clean, subcat_original_to_clean)
    services.save_json(
        paths.output_dir / "possible_subcats_by_brand.json", possible_subcats_by_brand
    )

    return brand_original_to_clean, subcat_original_to_clean, possible_subcats_by_brand


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
        clean_colors = product.get(keys.CLEAN_COLORS, [])
        color = select_color(clean_names, clean_colors)
        if color:
            product[keys.SELECTED_COLOR] = color

    return products


def skus_to_products(skus: dict):
    # only relevant keys remain
    skus = filter_docs(list(skus.values()))

    logging.info("add_raw_subcats..")
    # they have cats, add clean_cats and sub_cats
    skus = add_raw_subcats(skus)

    logging.info("group_products..")
    # group skus to products
    products = group_products(skus)

    logging.info("add_color..")
    products = add_color(products)

    return products


def add_sub_brand(products, possible_subcats_by_brand):
    products = add_filtered_names(products, possible_subcats_by_brand)
    filtered_names_tree = get_filtered_names_tree(products)
    # services.save_json(paths.filtered_names_tree, filtered_names_tree)

    possible_word_groups_for_sub_brand = create_possible_sub_brands(filtered_names_tree)
    products = select_subbrand(products, possible_word_groups_for_sub_brand)
    return products


def enrich_product_data(products, debug=False):
    # we may need to find the original of a clean string
    (
        brand_original_to_clean,
        subcat_original_to_clean,
        possible_subcats_by_brand,
    ) = get_indexes(products)

    brand_pool: set = get_brand_pool(products, possible_subcats_by_brand)
    # services.save_json(paths.brand_pool, sorted(list(brand_pool)))

    products = add_brand(products, brand_pool)

    products = add_subcat(products, subcat_original_to_clean)
    products = add_sub_brand(products, possible_subcats_by_brand)

    return products


def add_product_info_to_skus(skus: dict, products: list):
    keys_to_add = {keys.SUBCAT, keys.BRAND, keys.SUB_BRAND}
    product_info = {}
    for product in products:
        to_update = {k: product.get(k) for k in keys_to_add}
        if keys.PRODUCT_ID in product:
            pid = product.get(keys.PRODUCT_ID)
            product_info[pid] = to_update
        else:
            sku_id = product.get(keys.SKU_ID)
            skus[sku_id].update(to_update)

    for sku_id, sku in skus.items():
        if keys.PRODUCT_ID in sku:
            pid = sku.get(keys.PRODUCT_ID)
            skus[sku_id].update(product_info.get(pid))

    return skus


def add_brand_sub_brand_subcat_to_skus(skus: dict):
    products: list = skus_to_products(skus)
    products = enrich_product_data(products)
    add_product_info_to_skus(skus, products)
    return skus, products


def test_enrich(skus: dict):
    _, products = add_brand_sub_brand_subcat_to_skus(skus)
    inspect_results(products)
    analyze_brand(products)
    analyze_subcat(products)
    services.save_json(paths.products_out, products)


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)
    skus: dict = services.read_json(paths.skus)
    test_enrich(skus)
    print("done!")

    """

    + replace partials with reals in names, permanently -> replace sivi det with sivi deterjan
    + if no brand found in name, and no vendor given brand, search if name has a brand from the global pool 
    + if no subcat found in name, and no vendor given subcat, 
    search if name has a subcat from the global pool 
        + such products are also predicted with ML
        but having a subcat directly in name gives clearly better results than ML predictions 
    + cut off possible word groups for sub_brand from median, and filter out shorter than 3 letters 
    
    """
