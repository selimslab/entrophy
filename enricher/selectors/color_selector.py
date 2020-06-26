from cleaners.color_to_clean import get_color_original_to_clean
import paths as paths
import services
import constants as keys


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
