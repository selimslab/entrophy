import os
from collections import Counter
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

stopwords = {"ve", "ile", "for", "için", "veya", "li", "lu", "ml", "gr", "kg", "lt"}


def remove_brand(name: str, brands: List[str]):
    for brand in brands:
        if brand in name:
            name = name.replace(brand, "")

    return name


def remove_subcat(name: str, subcats: List[str]):
    for sub in subcats:
        if sub in name:
            name = name.replace(sub, "")
    return name


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
    filtered_tokens = [t for t in tokens if not is_known_token(t) and len(t) > 1]
    return " ".join(filtered_tokens)


def remove_size(name: str):
    all_matches = size_finder.get_all_matches(name + " ")
    for match in all_matches:
        name = name.replace(match, "")
    return name


def filter_out_knownword_groups_from_a_name(product):
    clean_names = product.get(keys.CLEAN_NAMES)
    brand_candidates = product.get(keys.BRAND_CANDIDATES)
    subcat_candidates = product.get(keys.SUBCAT_CANDIDATES)

    sorted_brands = sorted(brand_candidates.keys(), key=len, reverse=True)
    sorted_subcats = sorted(subcat_candidates.keys(), key=len, reverse=True)

    filtered_names = []
    for name in clean_names:
        name = remove_size(name)
        name = remove_brand(name, sorted_brands)
        name = remove_subcat(name, sorted_subcats)
        name = filter_tokens(name)
        if name:
            filtered_names.append(name)

    return filtered_names


def filter_all_products():
    products = services.read_json(
        output_dir / "products_with_brand_and_sub_cat.json"
    )
    for product in tqdm(products):
        filtered_names = filter_out_knownword_groups_from_a_name(product)
        print(filtered_names)
        product["filtered_names"] = filtered_names

    services.save_json(
        output_dir / "products_filtered.json",
        products
    )


if __name__ == "__main__":
    filter_all_products()