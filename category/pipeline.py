from tqdm import tqdm
import itertools
from collections import Counter
from typing import List, Dict
import os
import re

import services.collections_util
import services
import constants as keys

from paths import *

from data_services.mongo.collections import items_collection


def get_top_guesses(index, tokens):
    tokens_in_index = tuple(t for t in tokens if t in index)
    index_values = [index.get(t) for t in tokens]
    index_values = [set(c) for c in index_values if c]
    all_guesses = []
    for comb in itertools.combinations(index_values, 2):
        g = set.intersection(*comb)
        if g:
            all_guesses.append(list(g))

    if not all_guesses:
        all_guesses = [list(v) for v in index_values]

    candidates = services.collections_util.flatten(all_guesses)

    top_guess = None
    if all_guesses:
        top_guess = sorted(candidates, key=len)[0]
    if not top_guess and len(tokens_in_index) == 1:
        top_guess = tokens_in_index[0]

    return tokens_in_index, all_guesses, top_guess


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


def select_cat_and_brand(guess_docs, brand_index, cat_index):
    for doc in tqdm(guess_docs):
        tokens = doc.get("name_freq").keys()

        if "brand_freq" in doc:
            doc["brand"] = services.get_most_frequent_key(doc.get("brand_freq"))
        else:
            candidate_tokens, all_guesses, top_guess = get_top_guesses(
                brand_index, tokens
            )
            doc["brand_candidates"] = candidate_tokens
            doc["brand_all_guesses"] = all_guesses
            doc["top_brand_guess"] = top_guess

        if "subcat_freq" in doc:
            doc["cat"] = services.get_most_frequent_key(doc.get("subcat_freq"))
        else:
            candidate_tokens, all_guesses, top_guess = get_top_guesses(
                cat_index, tokens
            )
            doc["cat_candidates"] = candidate_tokens
            doc["cat_all_guesses"] = all_guesses
            doc["top_cat_guess"] = top_guess

    docs_with_brand_and_cat = [
        services.filter_empty_or_null_dict_values(doc) for doc in guess_docs
    ]

    return docs_with_brand_and_cat


def count_fields(docs: List[Dict], target_key):
    return sum(1 if target_key in doc else 0 for doc in docs)


def stat(docs):
    """ how many is guessed ? """
    with_brand = count_fields(docs, "brand")
    with_cat = count_fields(docs, "cat")

    with_brand_guess = count_fields(docs, "top_brand_guess")
    with_cat_guess = count_fields(docs, "top_cat_guess")

    print(
        with_brand, with_brand_guess, with_cat, with_cat_guess,
    )


def add_cat_and_brand():
    full_skus_path = temp / "full_skus.json"

    full_skus = services.read_json(full_skus_path)

    guess_docs = create_guess_docs(full_skus.values())

    services.save_json(guess_docs_path, guess_docs)

    brand_index = services.read_json(brand_index_path)
    cat_index = services.read_json(cat_index_path)

    docs_with_brand_and_cat = select_cat_and_brand(guess_docs, brand_index, cat_index)

    services.save_json(docs_with_brand_and_cat_path, docs_with_brand_and_cat)

    stat(docs_with_brand_and_cat)


def summarize_cats():
    docs_with_brand_and_cat = services.read_json(docs_with_brand_and_cat_path)
    catbr_summary = [
        {
            k: v
            for k, v in doc.items()
            if k in {"clean_names", "brand", "cat", "top_brand_guess", "top_cat_guess"}
        }
        for doc in docs_with_brand_and_cat
    ]
    services.save_json(catbr_summary_path, catbr_summary)

    stat(docs_with_brand_and_cat)


def list_to_clean_set(strs: list):
    res = services.clean_list_of_strings(strs)
    res = services.remove_null_from_list(res)
    res = sorted(list(set(res)))
    return res


def clean_cats_and_brands():
    cats = services.read_json("cleaner/joined_categories.json")
    cats = cats.get("categories")
    clean_cats = list_to_clean_set(cats)
    services.save_json("cleaner/clean_cats.json", clean_cats)

    brands = services.read_json("cleaner/joined_brands.json")
    brands = brands.get("brands")
    clean_brands = list_to_clean_set(brands)
    services.save_json("cleaner/clean_brands.json", clean_brands)


def get_ty_colors():
    ty_colors = items_collection.distinct("color", {keys.MARKET: "ty"})
    services.save_json(temp / "ty_colors.json", ty_colors)


def get_all_colors():
    color_path = temp / "colors.json"
    if not os.path.exists(color_path):
        colors = items_collection.distinct("color")
        print(colors)
        services.save_json(color_path, colors)
    else:
        colors = services.read_json(color_path)
    return colors


def clean_colors(colors):
    clean_colors = list_to_clean_set(colors)
    clean_colors = [c for c in clean_colors
                    if not c.isdigit() and "nocolor" not in c]

    letters_only = re.compile(r"[^a-z]")

    clean_colors = [
        " ".join(
            re.sub(letters_only, "", t).strip()
            for t in color.split()
        ).strip()
        for color in clean_colors
    ]
    clean_colors = list(set(clean_colors))
    clean_color_path = temp / "clean_colors.json"
    services.save_json(clean_color_path, clean_colors)


if __name__ == "__main__":
    ...
