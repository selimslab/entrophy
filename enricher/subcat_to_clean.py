import logging
from typing import List
import services
import constants as keys

from subcat_merger import get_merged_subcats


def search_gender(clean_sub):
    gender_dict = {
        "men": {"erkek", "men", "bay", "man"},
        "women": {"kadin", "women", "bayan", "woman"},
        "child": {"cocuk", "child", "children", "bebe"},
        "unisex": {"unisex"},
    }

    for gender, words in gender_dict.items():
        for gender_word in words:
            if services.full_string_search(clean_sub, gender_word):
                return gender_word


def is_bad_sub(clean_sub, clean_brands) -> bool:
    # filter out overly broad cats
    bads = {"indirim", "%", "kampanya"}

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
        "bebek",
        "kedi",
        "kopek",
        "bakim urun",
        "temizleyici",
    }
    return (
            clean_sub.isdigit()
            or len(clean_sub) > 40
            or any(bad in clean_sub for bad in bads)
            or clean_sub in too_broad
            or clean_sub in clean_brands
    )


def get_clean_sub(sub, merged_subs):
    clean_sub = services.clean_string(sub)
    clean_sub = services.plural_to_singular(clean_sub)
    if clean_sub in merged_subs:
        clean_sub = merged_subs.get(clean_sub)

    gender_word = search_gender(clean_sub)
    if gender_word:
        clean_sub = clean_sub.replace(gender_word, "").strip()

    return clean_sub, gender_word


def get_subcat_original_to_clean(products: List[dict], clean_brands: set) -> dict:
    logging.info("cleaning subcats..")

    subcat_original_to_clean = {}
    merged_subs = get_merged_subcats(products)

    for product in products:
        subcats = product.get(keys.SUB_CATEGORIES, [])
        clean_subcats = []
        for sub in subcats:
            clean_sub, gender_word = get_clean_sub(sub, merged_subs)
            if gender_word:
                product[keys.GENDER] = gender_word

            if is_bad_sub(clean_sub, clean_brands):
                continue

            clean_subcats.append(clean_sub)
            subcat_original_to_clean[sub] = clean_sub

        product[keys.CLEAN_SUBCATS] = clean_subcats

    return subcat_original_to_clean
