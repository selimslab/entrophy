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
    subcats = re.split("[/,&]", cat)
    return [s.strip() for s in subcats]


def test_cat_to_subcats():
    cases = [("Şeker,Tuz &Baharat / un ", ["Şeker", "Tuz", "Baharat", "un"])]
    services.check(cat_to_subcats, cases)


def filter_subcats(subcats):
    subcats = services.flatten(subcats)
    bads = {"indirim", "%"}
    subcats = [
        c for c in subcats if len(c) < 30 and not any(bad in c.lower() for bad in bads)
    ]
    subcat_lists = [cat_to_subcats(sub) for sub in subcats]
    subcats = services.flatten(subcat_lists)
    return subcats


def add_raw_subcats(skus: List[dict]):
    # derive_subcats_from_product_cats
    for sku in tqdm(skus):
        category_dict = sku.get(keys.CATEGORIES, {})
        subcats = []
        for market, cats in category_dict.items():
            if market == "ty":
                sub = cats[-1]
            elif isinstance(cats, str) and "/" in cats:
                sub = cats.split("/")[0]
            else:
                sub = cats
            subcats.append(sub)

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
                print("replace", partial_match, "with", sub)
                clean_names[i] = name

    # save replaced names
    product[keys.CLEAN_NAMES] = clean_names

    if subs:
        return subs[0]


def search_sub_in_names(vendor_subcats, clean_names):
    for sub in services.sorted_counter(vendor_subcats):
        for name in clean_names:
            if sub in name and set(name.split()).issuperset(set(sub.split())):
                return sub


def add_subcat(
        products: List[dict], subcat_original_to_clean: Dict[str, str],
):
    logging.info("adding subcat..")

    subcat_freq: Counter = get_subcat_freq(products, subcat_original_to_clean)
    services.save_json("out/subcat_freq.json", OrderedDict(subcat_freq.most_common()))

    not_in_name = 0
    from_sub = 0
    from_partial_sub = 0
    for product in tqdm(products):
        vendor_subcats = [
            subcat_original_to_clean.get(sub)
            for sub in product.get(keys.SUB_CATEGORIES, [])
        ]
        product[keys.CLEAN_SUBCATS] = vendor_subcats

        clean_names = product.get(keys.CLEAN_NAMES, [])
        if not clean_names:
            continue

        sub = search_sub_in_names(vendor_subcats, clean_names)
        partial_sub = search_and_replace_partial_subcat(product, vendor_subcats, clean_names)

        if sub:
            product[keys.SUBCAT] = sub
            from_sub += 1
        elif partial_sub:
            product[keys.SUBCAT] = partial_sub
            from_partial_sub += 1
        else:
            # filter out overly broad cats
            vendor_subcats = [
                s for s in vendor_subcats if s not in {"kozmetik", "supermarket"}
            ]
            if vendor_subcats:
                sub = services.get_most_common_item(vendor_subcats)
                product[keys.SUBCAT] = sub
                not_in_name += 1

                clean_names = product.get(keys.CLEAN_NAMES, [])
                print(clean_names)

                print(vendor_subcats)
                print(sub)

                print()

    print(from_sub, "subcats from_sub")
    print(from_partial_sub, "subcats from_partial_sub")
    print(not_in_name, "subcats not_in_name")
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


def get_possible_subcats_for_this_product(
        product: dict, possible_subcats_by_brand: dict, subcat_original_to_clean: dict
) -> list:
    """
    the result is a long list, every possible subcat for this brand and parts of this brand
    example:
        for brand loreal paris,
        include all possible subcats for both loreal and loreal paris

    """
    brand_candidates = product.get(keys.BRAND_CANDIDATES, [])
    possible_subcats = [
        possible_subcats_by_brand.get(brand, []) for brand in brand_candidates
    ]

    brand = product.get(keys.BRAND)
    # possible_subcats will be a union of possible_subcats for all start combinations
    # ["loreal", "loreal excellence", "loreal excellence intense"]
    if brand:
        brand_tokens = brand.split()
        for i in range(1, len(brand_tokens) + 1):
            possible_parent_brand = " ".join(brand_tokens[0:i])
            possible_subcats += possible_subcats_by_brand.get(possible_parent_brand, [])

    clean_subcats = get_clean_sub_categories(product, subcat_original_to_clean)
    possible_subcats += clean_subcats

    possible_subcats = list(services.flatten(possible_subcats))

    # dedup, remove very long sub_cats, they are mostly wrong
    possible_subcats = [
        s for s in possible_subcats if s and 1 < len(s) < 30 and "indirim" not in s
    ]

    return possible_subcats
