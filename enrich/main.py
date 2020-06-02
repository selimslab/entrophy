import multiprocessing
import os
from collections import defaultdict
from tqdm import tqdm
import logging
from typing import List, Iterable, Dict
import itertools

import services
import constants as keys
from paths import input_dir, output_dir

from mongo_service import get_raw_docs_with_markets_and_cats_only


def index_brands_and_subcats() -> tuple:
    """
        "finish": [
        "kirec onleyici",
        "bulasik yikama urunleri",
        ...
        ]

    """
    brand_subcats_pairs = defaultdict(set)
    clean_brand_original_brand_pairs = {}
    sub_cat_market_pairs = defaultdict(set)

    def update_brand_subcats_pairs(brands: Iterable, subcats: Iterable, market):
        brands = list(set(brands))
        subcats = list(set(subcats))

        clean_to_original = {services.clean_name(b): b for b in brands}
        clean_brand_original_brand_pairs.update(clean_to_original)
        clean_brands = set(b for b in clean_to_original.keys() if len(b) > 1)

        clean_subcats = services.clean_list_of_strings(subcats)
        clean_subcats = [sub for sub in clean_subcats if sub]

        for sub in clean_subcats:
            sub_cat_market_pairs[sub].add(market)

        for b in clean_brands:
            brand_subcats_pairs[b].update(clean_subcats)

    def add_ty():
        ty_raw = services.read_json(input_dir / "ty_raw.json")
        for main_cat, filters in ty_raw.items():
            brands: list = filters.get("brand")
            subcats: list = filters.get("category")
            update_brand_subcats_pairs(brands, subcats, keys.TRENDYOL)

    def add_watsons():
        watsons_raw = services.read_json(input_dir / "watsons_raw.json")
        for main_cat, filters in watsons_raw.items():
            brands = filters.get("marka")
            subcats = filters.get("cats")

            update_brand_subcats_pairs(brands, subcats, keys.WATSONS)

    def add_from_raw_docs():
        raw_docs_path = input_dir / "raw_docs.json"
        if not os.path.exists(raw_docs_path):
            cursor = get_raw_docs_with_markets_and_cats_only()
            raw_docs = list(cursor)
            services.save_json(raw_docs_path, raw_docs)
        else:
            raw_docs = services.read_json(raw_docs_path)

        for doc in raw_docs:
            brand = doc.get(keys.BRAND)
            cats = doc.get(keys.CATEGORIES, [])
            market = doc.get(keys.MARKET)

            brands = [brand]
            subcats = clean_sub_cats(cats)
            update_brand_subcats_pairs(brands, subcats, market)

    add_ty()
    add_watsons()
    add_from_raw_docs()
    return brand_subcats_pairs, clean_brand_original_brand_pairs, sub_cat_market_pairs


def clean_brands(brands: list) -> list:
    """
     johnson s baby -> johnsons baby
    """
    return services.clean_list_of_strings(services.flatten(brands))


def add_clean_brand(sku: dict) -> dict:
    sku[keys.CLEAN_BRANDS] = clean_brands(sku.get("brands", []))
    return sku


def clean_cats(cats: list) -> list:
    return services.clean_list_of_strings(services.flatten(cats))


def add_clean_cats(sku: dict) -> dict:
    cats = sku.get(keys.CATEGORIES, [])
    sku[keys.CLEAN_CATS] = clean_cats(cats)
    return sku


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

    # "bebek bezi/bebek, oyuncak" -> bebek bezi
    subcats = [sub.split("/")[0] for sub in subcats]

    # subcats = [sub.split(",")[-1] for sub in subcats]

    clean_subcats = services.clean_list_of_strings(services.flatten(subcats))
    return clean_subcats


def add_clean_subcats(sku: dict) -> dict:
    cats = sku.get(keys.CATEGORIES, [])
    sku[keys.CLEAN_SUBCATS] = clean_sub_cats(cats)
    return sku


def get_clean_skus(skus: List[dict]):
    relevant_keys = {keys.CATEGORIES, keys.BRANDS_MULTIPLE, keys.CLEAN_NAMES, keys.NAME}
    skus = [services.filter_keys(doc, relevant_keys) for doc in skus]

    with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
        skus = pool.map(add_clean_brand, tqdm(skus))
        skus = pool.map(add_clean_cats, tqdm(skus))
        skus = pool.map(add_clean_subcats, tqdm(skus))

    return skus


def get_first_token_freq(skus):
    names = [sku.get(keys.CLEAN_NAMES, []) for sku in skus]
    names = services.flatten(names)
    names = [n for n in names if n]
    first_tokens = [name.split()[0] for name in names]
    first_tokens = [n for n in first_tokens if len(n) > 2]

    first_token_freq = services.get_ordered_token_freq_of_a_nested_list(first_tokens)
    first_token_freq = {
        token: freq for token, freq in first_token_freq.items() if freq > 100
    }
    return first_token_freq


def get_brand_pool(brand_subcats_pairs: dict, skus) -> set:
    first_token_freq = get_first_token_freq(skus)
    services.save_json(output_dir / "first_token_freq.json", first_token_freq)
    brands_from_first_tokens = set(first_token_freq.keys())

    brand_pool = set(brand_subcats_pairs.keys())
    brand_pool.update(brands_from_first_tokens)

    return brand_pool


def filter_brands(brands: list) -> list:
    return [
        b
        for b in brands
        if len(b) > 2
           and not any(bad in b for bad in {"brn ", "markasiz", "erkek", "kadin"})
    ]


def select_brand(brand_candidates: list) -> str:
    # TODO beware position
    if brand_candidates:
        brand_candidates = list(set(brand_candidates))
        brand = sorted(brand_candidates, key=len)[-1]
        return brand


def get_brand_candidates(
        sku: dict, brands_with_multiple_tokens: set, brand_pool: set
) -> list:
    """
    find brand first,
    there only a few possible cats for this brand
    indexes should reflect that too

    johnson s baby -> johnsons baby
    """
    candidates = []
    candidates += sku.get(keys.CLEAN_BRANDS, [])

    clean_names = sku.get(keys.CLEAN_NAMES, [])

    # this search is 2 parts to make it faster,
    # we don't have to search every possible brand in name
    for name in clean_names:
        # search single-word brands
        # brand is in first two tokens mostly
        name_tokens = services.tokenize(name)
        first_token = name_tokens[0]
        if first_token in brand_pool:
            candidates.append(first_token)

        first_three_tokens_of_name = " ".join(name_tokens[:3])
        # search multiple-word brands
        for brand in brands_with_multiple_tokens:
            if brand in first_three_tokens_of_name:
                candidates.append(brand)

    candidates = filter_brands(candidates)
    return candidates


def add_brand_to_skus(clean_skus: List[dict], brand_subcats_pairs: dict):
    """
    0. cat and subcat are different things, beware
    1. clean well
    2. using ty_raw, wat_raw, and full skus  ->
    create
    brand : [possible cats]
    cat : [possible brands]

    so given a brand, the possible cats will be known
    """

    brand_pool = get_brand_pool(brand_subcats_pairs, clean_skus)
    brands_with_multiple_tokens = {b for b in brand_pool if len(b.split()) > 1}
    services.save_json(output_dir / "brand_pool.json", list(brand_pool))
    services.save_json(
        output_dir / "brands_with_multiple_tokens.json",
        list(brands_with_multiple_tokens),
    )

    for sku in tqdm(clean_skus):
        brand_candidates = get_brand_candidates(
            sku, brands_with_multiple_tokens, brand_pool
        )
        sku[keys.BRAND_CANDIDATES] = brand_candidates
        sku[keys.BRAND] = select_brand(brand_candidates)

    return clean_skus


def get_sku_summary(skus_with_brand_and_sub_cat: List[dict]) -> List[dict]:
    summary_keys = {keys.CLEAN_NAMES, keys.BRAND, keys.SUBCAT}
    summary = [
        services.filter_keys(doc, summary_keys) for doc in skus_with_brand_and_sub_cat
    ]
    for doc in summary:
        doc["names"] = list(set(doc.pop(keys.CLEAN_NAMES)))[:3]

    summary = [services.remove_null_dict_values(doc) for doc in summary]
    return summary


def select_subcat(
        sub_cat_candidates: list, sub_cat_market_pairs: Dict[str, list],
):
    if sub_cat_candidates:
        # prioritize markets
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
) -> List[dict]:
    for sku in tqdm(skus):
        sub_cat_candidates = []

        clean_names = sku.get(keys.CLEAN_NAMES, [])

        brand = sku.get(keys.BRAND)

        possible_subcats_for_this_brand = brand_subcats_pairs.get(brand, [])

        for sub in itertools.chain(sku.get(keys.CLEAN_SUBCATS, []), possible_subcats_for_this_brand):
            if any(sub in name for name in clean_names):
                sub_cat_candidates.append(sub)

        # dedup, remove very long sub_cats, they are mostly wrong
        sub_cat_candidates = list(
            set([s for s in sub_cat_candidates if s and len(s) < 15])
        )

        sku[keys.SUBCAT_CANDIDATES] = sub_cat_candidates
        if sub_cat_candidates:
            sku[keys.SUBCAT] = select_subcat(sub_cat_candidates, sub_cat_market_pairs)

    return skus


def create_subcat_index():
    brand_subcats_pairs = services.read_json(brand_subcats_pairs_path)

    subcat_index = defaultdict(dict)
    stopwords = {"ml", "gr", "adet", "ve", "and", "ile"}

    for brand, subcats in brand_subcats_pairs.items():
        subcat_index[brand] = services.create_inverted_index(set(subcats), stopwords)

    services.save_json(output_dir / "subcat_index.json", subcat_index)


def create_indexes():
    (
        brand_subcats_pairs,
        clean_brand_original_brand_pairs,
        sub_cat_market_pairs,
    ) = index_brands_and_subcats()

    sub_cat_market_pairs = services.convert_dict_set_values_to_list(
        sub_cat_market_pairs
    )
    services.save_json(output_dir / "sub_cat_market_pairs.json", sub_cat_market_pairs)

    brand_subcats_pairs = services.convert_dict_set_values_to_list(brand_subcats_pairs)
    services.save_json(brand_subcats_pairs_path, brand_subcats_pairs)
    services.save_json(
        output_dir / "clean_brand_original_brand_pairs.json",
        clean_brand_original_brand_pairs,
    )

    return brand_subcats_pairs, sub_cat_market_pairs


def enrich_sku_data(clean_skus: List[dict]):
    """
    1. clean and index brands + cats
        brand_subcats_pairs,
        clean_brand_original_brand_pairs,
        sub_cat_market_pairs,
    2. select a brand
        skus_with_brands
    3. select a category by restricting possible cats for this brand and prioritizing markets
        skus_with_brand_and_sub_cat
    """
    brand_subcats_pairs, sub_cat_market_pairs = create_indexes()

    # add brand
    skus_with_brands = add_brand_to_skus(clean_skus, brand_subcats_pairs)
    services.save_json(output_dir / "skus_with_brands.json", skus_with_brands)

    # add subcat
    skus_with_brand_and_sub_cat = add_sub_cat_to_skus(
        skus_with_brands, brand_subcats_pairs, sub_cat_market_pairs
    )
    services.save_json(
        output_dir / "skus_with_brand_and_sub_cat.json", skus_with_brand_and_sub_cat
    )

    name_brand_subcat = get_sku_summary(skus_with_brand_and_sub_cat)
    services.save_json(output_dir / "name_brand_subcat.json", name_brand_subcat)

    print("done!")


def count_fields(docs, target_key):
    return sum(1 if target_key in doc else 0 for doc in docs)


def inspect_results():
    docs = services.read_json(output_dir / "name_brand_subcat.json")

    without_brand_or_sub = [doc for doc in docs if keys.BRAND not in doc or keys.SUBCAT not in doc]
    services.save_json(output_dir / "without_brand_or_sub.json", without_brand_or_sub)

    with_brand_and_sub = [doc for doc in docs if keys.BRAND in doc and keys.SUBCAT in doc]
    services.save_json(output_dir / "with_brand_and_sub.json", with_brand_and_sub)

    brands_in_results = [doc.get(keys.BRAND) for doc in docs]
    subcats_in_results = [doc.get(keys.SUBCAT) for doc in docs]

    services.save_json(
        output_dir / "brands_in_results.json",
        sorted(services.dedup_denull(brands_in_results)),
    )
    services.save_json(
        output_dir / "subcats_in_results.json",
        sorted(services.dedup_denull(subcats_in_results)),
    )

    with_brand = count_fields(docs, keys.BRAND)
    with_sub = count_fields(docs, keys.SUBCAT)

    print(
        "total",
        len(docs),
        "\n",
        "with_brand",
        with_brand,
        "\n",
        "with_sub",
        with_sub,
        "\n",
        "without_brand_or_sub",
        len(without_brand_or_sub),
        "\n",
        "with_brand_and_sub",
        len(with_brand_and_sub),
        "\n",
    )


def add_gender(sku):
    ...


def add_color(sku):
    ...


def add_parent_cat(sku):
    ...


def refresh():
    skus = services.read_json(input_dir / "full_skus.json").values()
    clean_skus = get_clean_skus(skus)
    enrich_sku_data(clean_skus)
    inspect_results()


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)
    brand_subcats_pairs_path = output_dir / "brand_subcats_pairs.json"
    refresh()
    # inspect_brands()
