import collections
from dataclasses import asdict
import services
import constants as keys
import services
from pprint import pprint
from collections import defaultdict, Counter
from tqdm import tqdm
import itertools

all_brands = set()


def merge_ty():
    ty = services.read_json("filters/ty_filters2.json")

    merged = defaultdict(set)  # uses set to avoid duplicates

    for cat, filters in ty.items():
        for k, v in filters.items():  # use d.iteritems() in python 2
            merged[k].update(v)

    pprint(merged)

    brand = merged.get("brand")
    pprint(brand)
    print(len(brand))


def select_brand(docs, tokens):
    brands = [doc.get(keys.BRAND) for doc in docs]
    brands = set(n for n in brands if n)
    if brands:
        brand = collections.Counter(brands).most_common(1)[0][0]
        return brand
    else:
        for token in tokens:
            if token in all_brands:
                return token


def all_cats_and_brands():
    brands = services.read_json("cleaner/joined_brands.json")
    cats = services.read_json("cleaner/joined_categories.json")

    cats = cats.get("categories")
    print(len(cats))
    clean_cats = [services.clean_name(cat) for cat in cats]
    clean_cats = sorted(list(set(clean_cats)))
    services.save_json("cleaner/clean_cats.json", clean_cats)

    brands = brands.get("brands")
    clean_brands = [services.clean_name(b) for b in brands]
    clean_brands = sorted(list(set(clean_brands)))
    print(len(brands))

    services.save_json("cleaner/clean_brands.json", clean_brands)
