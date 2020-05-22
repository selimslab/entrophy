from tqdm import tqdm
from collections import Counter

import services.collections_util
import services
import constants as keys


def get_the_guess_doc(sku):
    cats = sku.get(keys.CATEGORIES, [])
    clean_cats = services.clean_list_of_strings(services.flatten(cats))
    cat_tokens = services.get_cleaned_tokens_of_a_nested_list(cats)
    subcats = []
    for cat in cats:
        if isinstance(cat, list):
            subcats.append(cat[-1])
        else:
            subcats.append(cat)

    subcats = [sub.split("/")[-1] for sub in subcats]
    subcat_tokens = services.get_cleaned_tokens_of_a_nested_list(subcats)

    brands = sku.get(keys.BRAND)
    clean_brands = services.clean_list_of_strings(services.flatten(brands))
    brand_tokens = services.get_cleaned_tokens_of_a_nested_list(brands)

    clean_names = sku.get("clean_names")
    name_tokens = services.get_cleaned_tokens_of_a_nested_list(clean_names)

    guess_doc = {
        # "names": sku.get("names"),
        "clean_names": clean_names,
        "cats": cats,
        "clean_cats": clean_cats,
        "subcats": subcats,
        "brands": brands,
        "clean_brands": clean_brands,
        "cat_freq": Counter(cat_tokens),
        "subcat_freq": Counter(subcat_tokens),
        "brand_freq": Counter(brand_tokens),
        "name_freq": Counter(name_tokens),
    }
    return guess_doc


def create_guess_docs(full_skus):
    guess_docs = [get_the_guess_doc(sku) for sku in tqdm(full_skus)]

    guess_docs = [services.filter_empty_or_null_dict_values(doc) for doc in guess_docs]

    return guess_docs
