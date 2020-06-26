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


def get_clean_colors(sku):
    colors = sku.get(keys.COLOR_PLURAL, [])
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


def get_color_original_to_clean(skus: List[dict]) -> dict:
    logging.info("cleaning colors..")
    color_original_to_clean = {}

    for sku in skus:
        clean_colors, original_to_clean = get_clean_colors(sku)
        color_original_to_clean.update(original_to_clean)
        sku[keys.CLEAN_COLORS] = clean_colors

    return color_original_to_clean
