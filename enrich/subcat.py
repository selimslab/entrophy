import re
import itertools
from typing import List, Dict
from collections import Counter
import logging
from tqdm import tqdm

import services
import constants as keys


def clean_sub_cats(cats: list) -> list:
    """
    her market için ayrı
    "okul kırtasiye, aksesuarları/kırtasiye/ev, pet" -> migros

    "bebek bezi/bebek, oyuncak" -> bebek bezi
    """

    subcats = []
    for cat in cats:
        if isinstance(cat, list):
            subcats.append(cat[-1])
        else:
            subcats.append(cat)

    # "bebek bezi/bebek, oyuncak" -> [ bebek bezi, bebek, oyuncak]
    # subcats = [sub.split("/") for sub in subcats]

    # "Şeker, Tuz, Baharat" ->  [Şeker, Tuz, Baharat]
    subcats = [re.split("/ |, |&", sub) for sub in subcats]

    clean_subcats = services.clean_list_of_strings(services.flatten(subcats))
    # clean_subcats = [sub for sub in clean_subcats if len(sub)>2]
    return clean_subcats


def select_subcat(
        sub_cat_candidates: list, sub_cat_market_pairs: Dict[str, list], subcat_freq: dict
):
    """ start from the longest and check if a subcat is in a prio. market, if not such found, return longest  """
    if sub_cat_candidates:
        subcat_candidates_with_freq = {
            sub: subcat_freq.get(sub, 0) for sub in sub_cat_candidates
        }
        sub = services.get_most_frequent_key(subcat_candidates_with_freq)
        return sub

        def prioritize_by_markets():
            priority_markets = [keys.TRENDYOL, keys.GRATIS, keys.WATSONS, keys.MIGROS]
            sorted_by_length = sorted(sub_cat_candidates, key=len, reverse=True)
            for sub in sorted_by_length:
                markets_for_this_sub = sub_cat_market_pairs.get(sub, [])
                if markets_for_this_sub and any(
                        m in priority_markets for m in markets_for_this_sub
                ):
                    return sub

            #  as a last resort, select longest
            sub_cat = sorted_by_length[0]
            return sub_cat


def add_sub_cat_to_skus(
        skus: List[dict],
        brand_subcats_pairs: Dict[str, list],
        sub_cat_market_pairs: Dict[str, list],
        subcat_freq: dict
) -> List[dict]:
    """
    There are a set of possible subcats for a given brand

    we check them if any of them is in any of the names of the given sku
    this leaves us with a few candidates

    then we choose prioritizing by market
    """
    logging.info("adding subcat..")
    for sku in tqdm(skus):
        sub_cat_candidates = []

        clean_names = sku.get(keys.CLEAN_NAMES, [])

        brand = sku.get(keys.BRAND)

        # for example,
        # for brand loreal excellence intense
        # possible_subcats will be a union of possible_subcats for all start combinations
        # ["loreal", "loreal excellence", "loreal excellence intense"]
        possible_subcats_for_this_brand = []
        if brand:
            brand_tokens = brand.split()
            for i in range(1, len(brand_tokens) + 1):
                possible_parent_brand = " ".join(brand_tokens[0:i])
                possible_subcats_for_this_brand += brand_subcats_pairs.get(
                    possible_parent_brand, []
                )

        for sub in itertools.chain(
                sku.get(keys.CLEAN_SUBCATS, []), possible_subcats_for_this_brand
        ):
            if any(sub in name for name in clean_names):
                sub_cat_candidates.append(sub)

        # dedup, remove very long sub_cats, they are mostly wrong, remove if it's also a brand
        sub_cat_candidates = list(
            set(
                s
                for s in sub_cat_candidates
                if s
                and 1 < len(s) < 30
                and "indirim" not in s
                and s not in brand_subcats_pairs
            )
        )

        sku[keys.SUBCAT_CANDIDATES] = dict(Counter(sub_cat_candidates))
        if sub_cat_candidates:
            sku[keys.SUBCAT] = select_subcat(sub_cat_candidates, sub_cat_market_pairs, subcat_freq)

    return skus
