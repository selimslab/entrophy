import multiprocessing
from collections import defaultdict
from tqdm import tqdm
import logging
from typing import List

import services
import constants as keys
from paths import input_dir, output_dir


def create_brand_subcats_pairs(clean_skus: List[dict]) -> tuple:
    """
        "finish": [
        "yumusaticilar",
        "p g urunleri",
        "genel temizlik urunleri",
        "bulasik tuzu",
        "hali ve tul yikama",
        "finish",
        "kirec onleyici",
        "bulasik yikama urunleri",
        ...
        ]

    """
    brand_subcats_pairs = defaultdict(set)
    clean_brand_original_brand_pairs = {}

    def update_brand_subcats_pairs(brands, subcats):
        clean_to_original = {services.clean_name(b): b for b in brands}
        clean_brand_original_brand_pairs.update(clean_to_original)
        clean_brands = set(b for b in clean_to_original.keys() if len(b) > 1)

        clean_subcats = services.clean_list_of_strings(subcats)
        clean_subcats = services.remove_empty_or_false_values_from_list(clean_subcats)

        for b in clean_brands:
            brand_subcats_pairs[b].update(clean_subcats)

    def add_ty():
        ty_raw = services.read_json(input_dir / "ty_raw.json")
        for main_cat, filters in ty_raw.items():
            brands = filters.get("brand")
            subcats = filters.get("category")
            update_brand_subcats_pairs(brands, subcats)

    def add_watsons():
        watsons_raw = services.read_json(input_dir / "watsons_raw.json")
        for main_cat, filters in watsons_raw.items():
            brands = set(filters.get("marka"))
            subcats = set(filters.get("cats"))

            update_brand_subcats_pairs(brands, subcats)

    def add_from_skus(skus):
        for sku in skus:
            brands = sku.get(keys.CLEAN_BRANDS, [])
            subcats = sku.get(keys.CLEAN_SUBCATS, [])
            update_brand_subcats_pairs(brands, subcats)

    add_ty()
    add_watsons()
    add_from_skus(clean_skus)
    return brand_subcats_pairs, clean_brand_original_brand_pairs


def create_subcat_brands_pairs() -> dict:
    ...


def clean_brands(sku):
    """
     johnson s baby -> johnsons baby
    """
    clean_brands = services.clean_list_of_strings(
        services.flatten(sku.get("brands", []))
    )
    sku[keys.CLEAN_BRANDS] = clean_brands
    return sku


def clean_cats(sku):
    cats = sku.get(keys.CATEGORIES, [])
    clean_cats = services.clean_list_of_strings(services.flatten(cats))
    sku[keys.CLEAN_CATS] = clean_cats
    return sku


def clean_sub_cats(sku):
    """
    "bebek bezi/bebek, oyuncak" -> oyuncak
    """

    subcats = []
    for cat in sku.get(keys.CATEGORIES, []):
        if isinstance(cat, list):
            subcats.append(cat[-1])
        else:
            subcats.append(cat)

    subcats = [sub.split("/")[-1] for sub in subcats]
    subcats = [sub.split(",")[-1] for sub in subcats]

    clean_subcats = services.clean_list_of_strings(services.flatten(subcats))
    sku[keys.CLEAN_SUBCATS] = clean_subcats
    return sku


def get_clean_skus(full_skus):
    skus = get_skus_with_relevant_fields(full_skus)

    with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
        skus = pool.map(clean_brands, tqdm(skus))
        skus = pool.map(clean_cats, tqdm(skus))
        skus = pool.map(clean_sub_cats, tqdm(skus))

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


def get_skus_with_relevant_fields(full_skus):
    relevant_keys = {keys.CATEGORIES, keys.BRANDS_MULTIPLE, keys.CLEAN_NAMES}
    skus = [services.filter_keys(doc, relevant_keys) for doc in full_skus.values()]

    return skus


def get_brand_pool(brand_subcats_pairs, skus):
    first_token_freq = get_first_token_freq(skus)
    services.save_json(output_dir / "first_token_freq.json", first_token_freq)

    brand_pool = set(brand_subcats_pairs.keys())
    brand_pool.update(set(first_token_freq.keys()))

    return brand_pool


def filter_brands(brands: list) -> list:
    return [
        b
        for b in brands
        if len(b) > 2 and not any(bad in b for bad in {"brn ", "markasiz", "erkek", })
    ]


def select_brand(brand_candidates: list) -> str:
    """
    HB-->TY-->Gratis-->Watsons--> Migros--> Random
    """
    if brand_candidates:
        brand_candidates = list(set(brand_candidates))
        brand = sorted(brand_candidates, key=len)[-1]
        return brand


def add_brand_to_skus(clean_skus: List[dict], brand_subcats_pairs: dict):
    """
    0. cat and subcat are different things, beware
    1. clean well
    2. using ty_raw, wat_raw, and full skus  ->
    create
    brand : [possible cats]
    cat : [possible brands]

    so given a brand, the possible cats will be known

    3.

    """

    def get_brand_candidates(sku: dict) -> list:
        """
        find brand first,
        there only a few possible cats for this brand
        indexes should reflect that too

        johnson s baby -> johnsons baby
        """
        brand_candidates = sku.get(keys.CLEAN_BRANDS, [])
        clean_names = sku.get(keys.CLEAN_NAMES, [])

        for name in clean_names:
            for brand in brand_pool:
                if brand in name:
                    brand_candidates.append(brand)

        brand_candidates = filter_brands(brand_candidates)
        return brand_candidates

    def get_brand(sku):
        brand_candidates = get_brand_candidates(sku)
        sku[keys.BRAND_CANDIDATES] = brand_candidates
        sku[keys.BRAND] = select_brand(brand_candidates)
        return sku

    brand_pool = get_brand_pool(brand_subcats_pairs, clean_skus)
    with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
        skus_with_brands = pool.map(get_brand, tqdm(clean_skus))

    return skus_with_brands


def add_sub_cat_to_skus(skus_with_brands: List[dict], brand_subcats_pairs: dict) -> List[dict]:
    return skus_with_brands


def enrich_sku_data():
    full_skus = services.read_json(input_dir / "full_skus.json")

    clean_skus = get_clean_skus(full_skus)

    # create and save brand subcat pairs
    brand_subcats_pairs, clean_brand_original_brand_pairs = create_brand_subcats_pairs(
        clean_skus
    )

    brand_subcats_pairs = services.convert_dict_set_values_to_list(brand_subcats_pairs)
    services.save_json(output_dir / "brand_subcats_pairs.json", brand_subcats_pairs)
    services.save_json(
        output_dir / "clean_brand_original_brand_pairs.json",
        clean_brand_original_brand_pairs,
    )

    skus_with_brands = add_brand_to_skus(clean_skus, brand_subcats_pairs)

    summarize(skus_with_brands)

    skus_with_brand_and_sub_cat = add_sub_cat_to_skus(skus_with_brands, brand_subcats_pairs)


def add_gender(sku):
    ...


def add_color(sku):
    ...


def add_parent_cat(sku):
    ...


def summarize(skus):
    summary_keys = {"brand", "clean_names"}
    skus = [services.filter_keys(doc, summary_keys) for doc in skus]
    for doc in skus:
        doc["name"] = doc.pop("clean_names")[0]
    skus_with_brand = [sku for sku in skus if "brand" in sku]
    skus_without_brand = [sku for sku in skus if "brand" not in sku]
    services.save_json(output_dir / "skus_with_brand.json", skus_with_brand)
    services.save_json(output_dir / "skus_without_brand.json", skus_without_brand)


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)
    enrich_sku_data()
