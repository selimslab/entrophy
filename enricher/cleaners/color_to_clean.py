import logging
from typing import List
import services
import constants as keys


def is_bad_color(clean_color):
    stopwords = {"nocolor", "no color", "cok renkli", "renkli"}
    return (
        not clean_color
        or clean_color.isdigit()
        or any(sw in clean_color for sw in stopwords)
    )


def get_clean_colors(product):
    colors = product.get(keys.COLOR, []) + product.get(keys.VARIANT_NAME, [])
    colors = services.flatten(colors)
    clean_colors = []
    original_to_clean = {}
    for color in colors:
        clean_color = services.clean_string(color)
        if is_bad_color(clean_color):
            continue
        original_to_clean[color] = clean_color
        clean_colors.append(clean_color)

    return clean_colors, original_to_clean


def get_color_original_to_clean(products: List[dict]) -> dict:
    logging.info("cleaning colors..")
    color_original_to_clean = {}

    for product in products:
        clean_colors, original_to_clean = get_clean_colors(product)
        color_original_to_clean.update(original_to_clean)
        product[keys.CLEAN_COLORS] = clean_colors

    return color_original_to_clean
