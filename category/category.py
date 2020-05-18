from tqdm import tqdm
import collections
from pprint import pprint
import services
import constants as keys

# Define recursive dictionary
from collections import defaultdict
import uuid

import services.collections_util


def tree():
    return defaultdict(tree)


def group_names():
    fullskus = services.read_json("all_docs/full_skus.json")

    names = [sku.get("names") for sku in fullskus.values()]

    services.save_json("../test/test_logs/old/name_groups.json", names)


def relevant_fields():
    skus = services.read_json("temp/full_skus.json")

    pairs = services.read_json("../test/test_logs/old/latest_clean_pairs.json")

    cats = []
    for sku_id, sku in tqdm(skus.items()):
        doc_ids = sku.get("doc_ids")
        docs = [pairs.pop(doc_id, {}) for doc_id in doc_ids]

        categories = [doc.get(keys.CATEGORIES) for doc in docs]
        categories = [c for c in categories if c]
        flat_cats = services.collections_util.flatten(cats)
        cat_tokens = services.get_tokens_of_a_nested_list(flat_cats)
        cat_token_freq = collections.Counter(cat_tokens)

        subcats = []
        for c in categories:
            if isinstance(c, list):
                subcat = c[-1].split("/")[-1]
                subcats.append(subcat)
            else:
                subcats.append(c)

        subcats = [services.clean_name(c).split() for c in subcats if c]
        flat_subcats = services.collections_util.flatten(subcats)
        cat_freq = collections.Counter(flat_subcats)

        brands = [doc.get(keys.BRAND) for doc in docs]
        brands = [c for c in brands if c]
        clean_brands = [services.clean_name(b) for b in brands if b]
        brand_freq = collections.Counter(clean_brands)

        clean_names = sku.get("clean_names")
        name_tokens = services.get_tokens_of_a_nested_list(clean_names)
        name_freq = collections.Counter(name_tokens)

        sku = {
            "names": sku.get("names"),
            "clean_names": clean_names,
            "name_freq": name_freq,
            "brands": brands,
            "brand_freq": brand_freq,
            "categories": categories,
            "cat_freq": cat_freq,
            "cat_token_freq": cat_token_freq,
            # "sku_id": id
        }

        if brand_freq:
            brand = max(brand_freq, key=brand_freq.get)
            sku["brand"] = brand
        if cat_freq:
            cat = max(cat_freq, key=cat_freq.get)
            sku["cat"] = cat

        sku = {k: v for k, v in sku.items() if k and v}
        cats.append(sku)

    services.save_json("../test/test_logs/latest/cat.json", cats)


def group_products():
    skus = services.read_json("../test/test_logs/latest/cat.json")
    groups = tree()

    for sku in tqdm(skus):
        digits_units = set(tuple(c) for c in sku.get("digits_units", []))
        sku["digits_units"] = tuple(digits_units)

        flat_cats = services.collections_util.flatten(sku.get("categories", []))
        cat_tokens = services.get_cleaned_tokens_of_a_nested_list(flat_cats)
        sku["cat_token_freq"] = collections.Counter(cat_tokens)

        product_id = sku.get("product_id") or str(uuid.uuid4())
        sku_id = sku.pop("sku_id")
        groups[product_id][sku_id] = sku

    services.save_json("groups.json", dict(groups))


def stat():
    skus = services.read_json("../test/test_logs/latest/cat.json")
    with_brand = sum(1 if "brand" in sku else 0 for sku in skus)
    print(with_brand)

    with_cat = sum(1 if "cat" in sku else 0 for sku in skus)
    print(with_cat)


if __name__ == "__main__":
    stat()

"""

raw_docs -> skus -> get_relevant_fields 


create brand and cat indexes 
"""
"""
137k SKU
57786 with brand + 32k brand guess = 70k
56982 with cat + 41k cat guess = 118k 
"""
