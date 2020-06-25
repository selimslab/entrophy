import logging
from typing import List
import services
import constants as keys


def is_bad_brand(clean_brand):
    to_filter_out = {"brn ", "markasiz", "erkek", "kadin", " adet"}
    wrong_brands = {"dr", "my"}
    return (
        not clean_brand
        or clean_brand in wrong_brands
        or any(bad in clean_brand for bad in to_filter_out)
    )


def get_clean_brands(product):
    brands = product.get(keys.BRANDS_MULTIPLE, [])
    clean_brands = []
    original_to_clean = {}
    for brand in brands:
        clean_brand = services.clean_string(brand)
        if is_bad_brand(clean_brand):
            continue
        if "loreal" in clean_brand and "loreal paris" not in clean_brand:
            clean_brand = clean_brand.replace("loreal", "loreal paris")
        original_to_clean[brand] = clean_brand
        clean_brands.append(clean_brand)
    return clean_brands, original_to_clean


def get_brand_original_to_clean(products: List[dict]):
    logging.info("cleaning brands..")
    brand_original_to_clean = {}

    for product in products:
        clean_brands, original_to_clean = get_clean_brands(product)
        brand_original_to_clean.update(original_to_clean)
        product[keys.CLEAN_BRANDS] = clean_brands
    return brand_original_to_clean
