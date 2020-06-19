import logging
from typing import List

import services
import constants as keys


def get_brand_original_to_clean(products: List[dict]):
    logging.info("cleaning brands..")
    brand_original_to_clean = {}
    to_filter_out = {"brn ", "markasiz", "erkek", "kadin", " adet"}

    for product in products:
        brands = product.get(keys.BRANDS_MULTIPLE, [])
        for brand in brands:
            if brand not in brand_original_to_clean:
                clean_brand = services.clean_string(brand)
                if any(bad in brand for bad in to_filter_out):
                    continue
                if clean_brand == "loreal":
                    clean_brand = "loreal paris"
                brand_original_to_clean[brand] = clean_brand

    return brand_original_to_clean


def get_subcat_original_to_clean(products: List[dict]) -> dict:
    logging.info("cleaning subcats..")
    subcat_original_to_clean = {}
    # filter out overly broad cats
    bads = {"indirim", "%"}
    too_broad = {"kozmetik", "supermarket", "gida", "el", "erkek"}
    for product in products:
        subcats = product.get(keys.SUB_CATEGORIES, [])
        clean_subcats = []
        for sub in subcats:
            clean_sub = services.clean_string(sub)
            clean_sub = services.plural_to_singular(clean_sub)
            if len(clean_sub) < 40 and not any(bad in clean_sub for bad in bads) and clean_sub not in too_broad:
                clean_subcats.append(clean_sub)
                subcat_original_to_clean[sub] = clean_sub

        product[keys.CLEAN_SUBCATS] = clean_subcats

    return subcat_original_to_clean


def get_color_original_to_clean(products: List[dict]) -> dict:
    logging.info("cleaning colors..")
    color_original_to_clean = {}
    stopwords = {"nocolor", "no color", "cok renkli", "renkli"}

    for product in products:
        colors = product.get(keys.COLOR, []) + product.get(keys.VARIANT_NAME, [])
        for color in colors:
            if color not in color_original_to_clean:
                clean_color = services.clean_string(color)
                if (
                    not clean_color
                    or clean_color.isdigit()
                    or any(sw in clean_color for sw in stopwords)
                ):
                    continue
                color_original_to_clean[color] = clean_color
    return color_original_to_clean
