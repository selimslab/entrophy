import logging
from typing import List

import services
import constants as keys


def get_brand_original_to_clean(products: List[dict]):
    logging.info("cleaning brands..")
    brand_original_to_clean = {}
    to_filter_out = {"brn ", "markasiz", "erkek", "kadin", " adet"}
    wrong_brands = {"dr", "my"}
    for product in products:
        brands = product.get(keys.BRANDS_MULTIPLE, [])
        clean_brands = []
        for brand in brands:
            clean_brand = services.clean_string(brand)
            if (
                    not clean_brand
                    or clean_brand in wrong_brands
                    or any(bad in clean_brand for bad in to_filter_out)
            ):
                continue
            if "loreal" in clean_brand and "loreal paris" not in clean_brand:
                clean_brand = clean_brand.replace("loreal", "loreal paris")
            brand_original_to_clean[brand] = clean_brand
            clean_brands.append(clean_brand)
        product[keys.CLEAN_BRANDS] = clean_brands
    return brand_original_to_clean


def get_subcat_original_to_clean(products: List[dict], clean_brands: set) -> dict:
    logging.info("cleaning subcats..")
    subcat_original_to_clean = {}
    # filter out overly broad cats
    bads = {"indirim", "%"}
    too_broad = {
        "kozmetik",
        "supermarket",
        "gida",
        "el",
        "erkek",
        "bakim",
        "icecek",
        "sivi",
        "kati",
    }
    gender_dict = {
        "men": {"erkek", "men", "bay", "man"},
        "women": {"kadin", "women", "bayan", "woman"}
    }
    for product in products:
        subcats = product.get(keys.SUB_CATEGORIES, [])
        clean_subcats = []
        for sub in subcats:
            clean_sub = services.clean_string(sub)
            clean_sub = services.plural_to_singular(clean_sub)

            for gender, words in gender_dict.items():
                for word in words:
                    if word in clean_sub:
                        clean_sub = clean_sub.replace(word, "")
                        product[keys.GENDER] = gender
                        break

            if (
                    len(clean_sub) < 40
                    and not any(bad in clean_sub for bad in bads)
                    and clean_sub not in too_broad
                    and clean_sub not in clean_brands
            ):
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
        colors = services.flatten(colors)
        clean_colors = []

        for color in colors:
            clean_color = services.clean_string(color)
            if (
                    not clean_color
                    or clean_color.isdigit()
                    or any(sw in clean_color for sw in stopwords)
            ):
                continue
            color_original_to_clean[color] = clean_color
            clean_colors.append(clean_color)

        product[keys.CLEAN_COLORS] = clean_colors

    return color_original_to_clean
