from collections import Counter
import logging
import itertools

from tqdm import tqdm

import services
import constants as keys

men = {"erkek", "men", "bay", "man"}
woman = {"kadin", "women", "bayan", "woman"}
child = {"cocuk", "child", "children", "bebe"}
unisex = {"unisex"}

gender = set(itertools.chain.from_iterable([men, woman, child, unisex]))

color_pairs = [
    ("blue", "mavi"),
    ("beyaz", "white"),
    ("siyah", "black"),
    ("kirmizi", "red"),
    ("altin", "gold"),
    ("yellow", "sari"),
    ("green", "yesil"),
    ("dark", "koyu"),
]

color_dict = {}

for pair in color_pairs:
    color_dict[pair[0]] = pair[1]
    color_dict[pair[1]] = pair[0]

stopwords = {
    "ve",
    "and",
    "ile",
    "adet",
    "for",
    "icin",
    "veya",
    "li",
    "lu",
    "ml",
    "gr",
    "kg",
    "lt",
}


def remove_a_list_of_strings(s: str, to_remove: list):
    tokens = s.split()
    for word in to_remove:
        #  a string should include all tokens of the removal string
        if word in s and set(tokens).issuperset(word.split()):
            s = s.replace(word, "")
        # remove tokens
        for token_to_remove in word.split():
            if s and token_to_remove in tokens:
                s = s.replace(token_to_remove, "")
    return s


def remove_color(s, clean_colors):
    for color in clean_colors:
        #
        if color in s and set(s.split()).issuperset(color.split()):
            s = s.replace(color, "").strip()
        # remove sub tokens
        for token in color.split():
            if s and token in s:
                s = s.replace(token, "").strip()
            if s and token in color_dict:
                s = s.replace(color_dict.get(token), "")
    return s


def is_known_token(s: str):
    return services.is_barcode(s) or s in gender or s in stopwords


def filter_tokens(name: str):
    filtered_tokens = [t.strip() for t in name.split() if not is_known_token(t)]
    # filtered_tokens = [t for t in filtered_tokens if len(t) > 1 and t.isalnum()]
    return " ".join(filtered_tokens)


def filter_out_known_word_groups_from_a_name(product):
    """
    remove brand candidates, subcat_candidates, color, gender, plural_to_singular

    remove tokens like fsf343

    remove stopwords {"ve", "ile", "for", "icin", "veya", "li", "lu", "ml", "gr", "kg", "lt"}

    remove gender
        men = {"erkek", "men", "bay", "man"}
        woman = {"kadin", "women", "bayan", "woman"}
        child = {"cocuk", "child", "children", "bebe"}
        unisex = {"unisex"}

        remove len(s) > 4 and s.isdigit()

    remove non-alphanumeric chars

    remove single letters

    remove colors

    """

    # clean_colors = services.read_json(paths.clean_colors).values()

    clean_names = product.get(keys.CLEAN_NAMES, [])
    brand_candidates = product.get(keys.BRAND_CANDIDATES, [])
    subcat_candidates = product.get(keys.SUBCAT_CANDIDATES, [])
    clean_colors = product.get(keys.CLEAN_COLORS, [])

    # sorted by length to remove longest ones first
    sorted_brands = services.sort_from_long_to_short(set(brand_candidates))
    sorted_subcats = services.sort_from_long_to_short(set(subcat_candidates))
    sorted_colors = services.sort_from_long_to_short(set(clean_colors))

    filtered_names = []
    for name in clean_names:
        name = remove_a_list_of_strings(name, sorted_brands)
        name = remove_a_list_of_strings(name, sorted_subcats)
        name = remove_color(name, sorted_colors)
        name = filter_tokens(name)
        if name:
            filtered_names.append(name)

    return filtered_names


def add_filtered_names(products):
    logging.info("add_filtered_names..")
    for product in tqdm(products):
        filtered_names = filter_out_known_word_groups_from_a_name(product)
        product["filtered_names"] = filtered_names

    return products


if __name__ == "__main__":
    ...
