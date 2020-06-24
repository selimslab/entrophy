import re
from typing import List, Dict, Union, Iterable
from collections import defaultdict, Counter, OrderedDict
import logging
from pprint import pprint
from tqdm import tqdm

import services
import constants as keys

from freq import get_subcat_freq


def cat_to_subcats(cat: Union[list, str]) -> List[str]:
    # "Şeker, Tuz & Baharat / un " ->  [Şeker, Tuz, Baharat, un]
    subcats = re.split("/|,|&| ve | and ", cat)
    return [s.strip() for s in subcats]


def test_cat_to_subcats():
    cases = [("Şeker,Tuz &Baharat / un ve poveta and to", ["Şeker", "Tuz", "Baharat", "un", "poveta", "to"])]
    services.check(cat_to_subcats, cases)


def filter_subcats(subcats):
    subcats = services.flatten(subcats)
    subcat_lists = [cat_to_subcats(sub) for sub in subcats]
    subcats = services.flatten(subcat_lists)
    return subcats


def add_raw_subcats(skus: List[dict]):
    # derive_subcats_from_product_cats
    for sku in tqdm(skus):
        category_dict = sku.get(keys.CATEGORIES, {})
        subcats = []
        myos = []
        for market, cats in category_dict.items():
            if market in keys.MARKETYO_MARKET_NAMES:
                myos += cats
            elif market == "ty":
                sub = cats[-1]
            elif isinstance(cats, str) and "/" in cats:
                sub = cats.split("/")[0]
            else:
                sub = cats

            if sub:
                subcats.append(sub)

        # merge myos
        subcats += list(set(myos))
        sku[keys.SUB_CATEGORIES] = filter_subcats(subcats)
    return skus


def search_and_replace_partial_subcat(product, vendor_subcats, clean_names):
    """ a subcat might be written wrong, or abbreviated """
    subs = []
    for sub in services.sorted_counter(vendor_subcats):
        for i, name in enumerate(clean_names):
            if sub in name:
                continue
            # partial search
            # der hij -> derinlemesine hijyen
            partial_match = services.partial_string_search(name, sub)
            if partial_match:
                subs.append(sub)
                # replace partial_match with found subcat
                # der hij -> derinlemesine hijyen
                name = name.replace(partial_match, sub)
                clean_names[i] = name

    # save replaced names
    product[keys.CLEAN_NAMES] = clean_names

    if subs:
        return subs[0]


def search_sub_in_names(vendor_subcats, clean_names):
    for sub in services.sorted_counter(vendor_subcats):
        for name in clean_names:
            if services.full_string_search(name, sub):
                return sub
            if len(sub.split()) > 1 and sub in name:
                return sub


def search_in_global(clean_names, vendor_subcat_count):
    subs = []
    for name in clean_names:
        name_tokens = set(name.split())
        name_permutations = services.string_sliding_windows(name)
        for perm in name_permutations:
            if perm in vendor_subcat_count and name_tokens.issuperset(
                    set(perm.split())
            ):
                subs.append(perm)
    if subs:
        sub = services.sort_from_long_to_short(subs)[0]
        return sub


def add_subcat(
        products: List[dict], subcat_original_to_clean: Dict[str, str],
):
    logging.info("adding subcat..")

    vendor_subcat_count: Counter = get_subcat_freq(products, subcat_original_to_clean)
    services.save_json(
        "out/vendor_subcat_count.json", OrderedDict(vendor_subcat_count.most_common())
    )

    for product in tqdm(products):

        clean_names = product.get(keys.CLEAN_NAMES, [])
        if not clean_names:
            continue

        clean_subcats = product.get(keys.CLEAN_SUBCATS, [])
        sub = search_sub_in_names(clean_subcats, clean_names)
        partial_sub = search_and_replace_partial_subcat(
            product, clean_subcats, clean_names
        )

        if sub:
            product[keys.SUBCAT] = sub
            product[keys.SUBCAT_SOURCE] = "local_name"
        elif partial_sub:
            product[keys.SUBCAT] = partial_sub
            product[keys.SUBCAT_SOURCE] = "partial"
        elif clean_subcats:
            sub = services.get_majority_if_exists(clean_subcats)
            if sub:
                product[keys.SUBCAT] = sub
                product[keys.SUBCAT_SOURCE] = "majority"

        if keys.SUBCAT not in product:
            sub = search_in_global(clean_names, vendor_subcat_count)
            if sub:
                product[keys.SUBCAT] = sub
                product[keys.SUBCAT_SOURCE] = "global_name"

    logging.info("subcat stage report")
    stages = {"global_name", "local_name", "majority", "partial"}
    for stage in stages:
        res = sum(p.get(keys.SUBCAT_SOURCE) == stage for p in products)
        print(res, stage)

    return products


def get_possible_subcats_by_brand(
        products, brand_original_to_clean, subcat_original_to_clean
) -> Dict[str, list]:
    """ which subcats are possible for this brand

    "ariel": [
        "sivi jel deterjan",
        "camasir yikama urunleri",
        ...
    ]
    """
    possible_subcats_by_brand = defaultdict(set)

    for product in products:
        brands = product.get(keys.BRANDS_MULTIPLE, [])
        subcats = product.get(keys.SUB_CATEGORIES, [])

        clean_brands = (brand_original_to_clean.get(b) for b in brands)
        clean_subcats = (subcat_original_to_clean.get(s) for s in subcats)

        for clean_brand in clean_brands:
            possible_subcats_by_brand[clean_brand].update(set(clean_subcats))

    possible_subcats_by_brand = {
        k: list(v) for k, v in possible_subcats_by_brand.items()
    }
    return possible_subcats_by_brand


def get_clean_sub_categories(product, subcat_original_to_clean):
    """ vendor-given categories turned to subcats through splitting by / & , and cleaning """
    return [
        subcat_original_to_clean.get(sub)
        for sub in product.get(keys.SUB_CATEGORIES, [])
    ]
