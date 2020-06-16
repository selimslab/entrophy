import logging
from typing import List

import services
import constants as keys


def get_brand_original_to_clean(products: List[dict]):
    logging.info("cleaning brands..")
    brand_original_to_clean = {}

    for product in products:
        brands = product.get(keys.BRANDS_MULTIPLE, [])
        for brand in brands:
            if brand not in brand_original_to_clean:
                brand_original_to_clean[brand] = services.clean_string(brand)

    return brand_original_to_clean


def get_subcat_original_to_clean(products: List[dict]) -> dict:
    logging.info("cleaning subcats..")
    subcat_original_to_clean = {}
    for product in products:
        subcats = product.get(keys.SUB_CATEGORIES, [])
        for sub in subcats:
            if sub not in subcat_original_to_clean:
                clean_sub = services.clean_string(sub)
                clean_sub = services.plural_to_singular(clean_sub)
                subcat_original_to_clean[sub] = clean_sub
    return subcat_original_to_clean
