import re
from typing import List, Union
from tqdm import tqdm
from collections import defaultdict

import services
import constants as keys


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

    subcats = defaultdict(list)
    # only 1 vote per vendor
    for market, cats in category_dict.items():
        if market == "ty":
            sub = cats[-1]
        elif isinstance(cats, str) and "/" in cats:
            sub = cats.split("/")[0]
        else:
            sub = cats
        if sub:
            subcats[market].append(sub)

    subcats = {market: list(set(unfold_cats(subs))) for market, subs in subcats.items()}

    return subcats


def add_raw_subcats(skus: List[dict]):
    # derive_subcats_from_product_cats
    for sku in tqdm(skus):
        clean_cats = get_cats(sku)
        subcats = get_subcats(sku)
        sku[keys.CLEAN_CATS] = clean_cats
        if keys.PRODUCT_ID in sku:
            sku[keys.SUB_CATEGORIES] = subcats
        else:
            """

            SUB_CATEGORIES is a dict of market:subs pairs 

            it is done this way to ensure when multiple SKUs merged, 
            a vendor will vote only 1 subcat per product 
            {
                market_name: subs,
                ..
            }
            """
            subs = sku.get(keys.SUB_CATEGORIES, {}).values()
            sku[keys.SUB_CATEGORIES] = services.flatten(list(subs))

    return skus
