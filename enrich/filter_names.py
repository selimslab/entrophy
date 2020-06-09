import os
from collections import Counter, OrderedDict, defaultdict
import logging
from typing import List
import itertools

from tqdm import tqdm

import services
from paths import output_dir
from services.size_finder import size_finder
import constants as keys

men = {"erkek", "men", "bay", "man"}
woman = {"kadin", "women", "bayan", "woman"}
child = {"cocuk", "child", "children", "bebe"}
unisex = {"unisex"}

gender = set(itertools.chain.from_iterable([men, woman, child, unisex]))

color = {
    "mavi",
    "blue",
    "beyaz",
    "white",
    "siyah",
    "black",
    "kirmizi",
    "red",
    "altin",
    "gold",
    "yellow",
    "sari",
    "green",
    "yesil",
}

stopwords = {"ve", "ile", "for", "icin", "veya", "li", "lu", "ml", "gr", "kg", "lt"}


def remove_a_list_of_strings(s: str, to_remove: list):
    for bad in to_remove:
        if bad in s:
            s = s.replace(bad, "")
    return s


def is_barcode(s: str):
    return len(s) > 4 and s.isdigit()


def is_mixed_letters_and_words(s: str):
    """ nonsense like adas42342 """
    return len(s) > 5 and (s.isalnum() and not s.isdigit() and not s.isalpha())


def is_gender(s: str):
    return s in gender


def is_color(s: str):
    return s in color


def is_stopword(s: str):
    return s in stopwords


def is_known_token(s: str):
    return (
            is_barcode(s)
            or is_gender(s)
            or is_color(s)
            or is_stopword(s)
            or is_mixed_letters_and_words(s)
    )


def filter_tokens(name: str):
    tokens = name.split()
    filtered_tokens = [t.strip() for t in tokens if not is_known_token(t)]
    filtered_tokens = [t for t in filtered_tokens if len(t) > 1 and t.isalnum()]
    return " ".join(filtered_tokens)


def remove_size(name: str):
    all_matches = size_finder.get_all_matches(name + " ")
    for match in all_matches:
        name = name.replace(match, "")
    return name


def filter_out_knownword_groups_from_a_name(product, clean_colors):
    clean_names = product.get(keys.CLEAN_NAMES)
    brand_candidates = product.get(keys.BRAND_CANDIDATES)
    subcat_candidates = product.get(keys.SUBCAT_CANDIDATES)

    sorted_brands = sorted(brand_candidates.keys(), key=len, reverse=True)
    sorted_subcats = sorted(subcat_candidates.keys(), key=len, reverse=True)

    filtered_names = []
    for name in clean_names:
        name = remove_size(name)
        name = remove_a_list_of_strings(name, sorted_brands)
        name = remove_a_list_of_strings(name, sorted_subcats)
        name = remove_a_list_of_strings(name, clean_colors)
        name = filter_tokens(name)
        if name:
            filtered_names.append(name)

    return filtered_names


def filter_all_products():
    products = services.read_json(
        output_dir / "products_with_brand_and_sub_cat.json"
    )

    clean_colors = services.read_json(output_dir / "clean_colors.json")
    clean_colors = sorted(list(clean_colors), key=len, reverse=True)

    for product in tqdm(products):
        filtered_names = filter_out_knownword_groups_from_a_name(product, clean_colors)
        filtered_names = Counter(filtered_names)
        print(filtered_names)
        product["filtered_names"] = filtered_names

    services.save_json(
        output_dir / "products_filtered.json",
        products
    )


def create_sub_brand_tree(products_filtered):
    """cat: { sub_cat : { type: {brand: {sub_brand : [products] } }"""

    tree = {}
    logging.info("create_sub_brand_tree..")

    for product in tqdm(products_filtered):
        brand, subcat = product.get(keys.BRAND), product.get(keys.SUBCAT)

        if not (brand and subcat):
            continue

        filtered_names = product.get("filtered_names")
        if not filtered_names:
            continue

        if subcat not in tree:
            tree[subcat] = {}
        if brand not in tree[subcat]:
            tree[subcat][brand] = []

        tree[subcat][brand].append(filtered_names)

    return tree


def save_sub_tree():
    products = services.read_json(
        output_dir / "products_filtered.json",
    )
    sub_brand_tree = create_sub_brand_tree(products)
    services.save_json(output_dir / "sub_brand_tree.json", sub_brand_tree)


if __name__ == "__main__":
    # filter_all_products()
    # save_sub_tree()
    ...
