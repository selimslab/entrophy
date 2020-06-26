from typing import List, Dict
from collections import defaultdict, Counter, OrderedDict
import logging
from tqdm import tqdm

import services
import constants as keys

from prep.freq import get_subcat_freq

from predictors.subcat_predictor import get_subcat_predictions


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
            if perm in vendor_subcat_count and name_tokens.issuperset(set(tokens)):
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

    partial_sub = search_and_replace_partial_subcat(product, clean_subcats, clean_names)

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
    stages = {"global_name", "local_name", "majority", "partial", "ml"}
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
            "../out/vendor_subcat_count.json",
            OrderedDict(vendor_subcat_count.most_common()),
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

    subcat_predictions = get_subcat_predictions(products)
    for product in products:
        uid = product.get(keys.PRODUCT_ID) or product.get(keys.SKU_ID)
        if keys.SUBCAT not in product and uid in subcat_predictions:
            product[keys.SUBCAT] = subcat_predictions.get(uid)
            product[keys.SUBCAT_SOURCE] = "ml"

    stage_report(products)
    return products


