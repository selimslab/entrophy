import logging
from typing import List
from collections import defaultdict, Counter, OrderedDict
import itertools

import services
import constants as keys
import paths as paths


def sort_subcat():
    # sort by most common
    subcat_freq = services.read_json("out/subcat_freq.json")
    services.save_json(
        "out/subcat_freq.json", OrderedDict(Counter(subcat_freq).most_common())
    )


def analyze_subcat(products):
    # which subcats are assigned ?
    subcats_assigned = [p.get(keys.SUBCAT) for p in products]
    subcats_assigned = services.flatten(subcats_assigned)
    # subcats_assigned = list(set(subcats_assigned))

    # by which freq
    services.save_json(
        "out/subcats_assigned.json",
        OrderedDict(Counter(subcats_assigned).most_common()),
    )
    return subcats_assigned


def analyze_brand(products):
    # which brands are assigned ?
    brands_assigned = [p.get(keys.BRAND) for p in products]
    brands_assigned = services.flatten(brands_assigned)
    # by which freq
    services.save_json(
        "out/brands_assigned.json", OrderedDict(Counter(brands_assigned).most_common())
    )
    # with_brand_only = services.read_json(paths.output_dir / "with_brand_only.json")
    return brands_assigned


def how_many_with_vendor_brand(products):
    with_vendor_brand = sum(1 if p.get("brands") else 0 for p in products)
    print(with_vendor_brand)


def stages(products):
    relevant_keys = {
        keys.PRODUCT_ID,
        keys.SKU_ID,
        keys.SUBCAT,
        keys.CLEAN_NAMES,
        keys.BRAND,
        keys.SUBCAT_SOURCE,
    }
    products = [services.filter_keys(p, relevant_keys) for p in products]
    keyfunc = lambda product: product.get(keys.SUBCAT_SOURCE, "")
    products = sorted(products, key=keyfunc)
    for key, items in itertools.groupby(products, key=keyfunc):
        services.save_json("stage/" + key + ".json", list(items))


if __name__ == "__main__":
    # products = services.read_json(paths.products_out)
    from pprint import pprint

    new = services.read_json("out/subcats_assigned.json")
    merged = get_merged_subcats(new)
    pprint(merged)
