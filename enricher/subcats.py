import re
from typing import List, Dict, Union
from collections import defaultdict, Counter, OrderedDict
import logging
from tqdm import tqdm

import services
import constants as keys

from freq import get_subcat_freq


def cat_to_subcats(cat: Union[list, str]) -> List[str]:
    # "Şeker, Tuz & Baharat / un " ->  [Şeker, Tuz, Baharat, un]
    subcats = re.split("/|,|&| ve | and ", cat)
    return [s.strip() for s in subcats]


def test_cat_to_subcats():
    cases = [
        (
            "Şeker,Tuz &Baharat / un ve poveta and to",
            ["Şeker", "Tuz", "Baharat", "un", "poveta", "to"],
        )
    ]
    services.check(cat_to_subcats, cases)


def unfold_cats(subcats):
    """ [ "a/b&c", ["x and y", .. ], .. ] -> [a,b,c,x,y, .. ]"""
    subcats = services.flatten(subcats)
    subcat_lists = [cat_to_subcats(sub) for sub in subcats]
    subcats = services.flatten(subcat_lists)
    return subcats


def get_cats(sku):
    category_dict = sku.get(keys.CATEGORIES, {})

    cats = list(cats for market, cats in category_dict.items())
    cats = unfold_cats(cats)
    clean_cats = [services.clean_string(cat) for cat in cats]
    clean_cats = [services.plural_to_singular(cat) for cat in clean_cats]

    return clean_cats


def get_subcats(sku):
    category_dict = sku.get(keys.CATEGORIES, {})

    subcats = []
    myos = []
    for market, cats in category_dict.items():
        sub = None
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
    subcats = unfold_cats(subcats)

    return subcats


def add_raw_subcats(skus: List[dict]):
    # derive_subcats_from_product_cats
    for sku in tqdm(skus):
        clean_cats = get_cats(sku)
        subcats = get_subcats(sku)
        sku[keys.CLEAN_CATS] = clean_cats
        sku[keys.SUB_CATEGORIES] = subcats
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
                # der. hij. -> derinlemesine hijyen
                name = name.replace(partial_match, sub)
                clean_names[i] = name

    # save replaced names
    product[keys.CLEAN_NAMES] = clean_names

    if subs:
        return subs[0]


def search_parents(clean_cats, clean_names):
    """
    # Hiyerarşideki son elemanı subcat'ten bulduktan sonra ile majority öncesinde,
    # tüm hiyerarşiyi product içinde arayalım.

    Örnek:['Saç Spreyi', 'Saç Şekillendirici', 'Kişisel Bakım', 'Süpermarket', 'Saç Bakım']
    Bütün vendor'ların hiyerarşi son elemanını aradıktan sonra hala bulamadıysak,
    buradaki tüm 5'liyi product içinde arayıp, bulduğumuzu subcat olarak atıyoruz.
    """
    for cat in services.sort_from_long_to_short(list(set(clean_cats))):
        for name in clean_names:
            if services.full_string_search(name, cat):
                return cat
            # "kedi mama" in "kedi mamasi"
            if len(cat.split()) > 1 and cat in name:
                return cat


def search_sub_in_names(vendor_subcats, clean_names):
    for sub in services.sorted_counter(vendor_subcats):
        for name in clean_names:
            if services.full_string_search(name, sub):
                return sub
            # "kedi mama" in "kedi mamasi"
            if len(sub.split()) > 1 and sub in name:
                return sub


def search_in_global(clean_names, vendor_subcat_count):
    subs = []
    for name in clean_names:
        name_tokens = set(name.split())
        name_permutations = services.string_sliding_windows(name)
        for perm in name_permutations:
            tokens = perm.split()
            if len(tokens) < 2:
                continue
            if perm in vendor_subcat_count and name_tokens.issuperset(
                    set(tokens)
            ):
                subs.append(perm)
    if subs:
        sub = services.sort_from_long_to_short(subs)[0]
        return sub


def get_subcat_and_source(product):
    clean_names = product.get(keys.CLEAN_NAMES, [])
    if not clean_names:
        return

    clean_subcats = product.get(keys.CLEAN_SUBCATS, [])
    clean_cats = product.get(keys.CLEAN_CATS, [])

    # search last elements of vendor given lists
    sub = search_sub_in_names(clean_subcats, clean_names)
    if not sub:
        # search parents
        sub = search_sub_in_names(clean_cats, clean_names)

    partial_sub = search_and_replace_partial_subcat(
        product, clean_subcats, clean_names
    )

    if sub:
        return sub, "local_name"
    elif partial_sub:
        return partial_sub, "partial"
    elif clean_subcats:
        sub = services.get_majority_if_exists(clean_subcats)
        if sub:
            return sub, "majority"


def stage_report(products):
    logging.info("subcat stage report")
    stages = {"global_name", "local_name", "majority", "partial"}
    for stage in stages:
        res = sum(p.get(keys.SUBCAT_SOURCE) == stage for p in products)
        print(res, stage)


def add_subcat(
        products: List[dict], subcat_original_to_clean: Dict[str, str], debug=False
):
    logging.info("adding subcat..")

    vendor_subcat_count: Counter = get_subcat_freq(products, subcat_original_to_clean)
    if debug:
        services.save_json(
            "out/vendor_subcat_count.json", OrderedDict(vendor_subcat_count.most_common())
        )

    for product in tqdm(products):
        result = get_subcat_and_source(product)
        if result:
            sub, source = result
        else:
            clean_names = product.get(keys.CLEAN_NAMES, [])
            sub = search_in_global(clean_names, vendor_subcat_count)
            source = "global_name"

        if sub and source:
            product[keys.SUBCAT] = sub
            product[keys.SUBCAT_SOURCE] = source

    stage_report(products)
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

