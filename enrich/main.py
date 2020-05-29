import multiprocessing
from collections import defaultdict
from tqdm import tqdm
import logging

import services
import constants as keys
from paths import input_dir, output_dir


def clean_brands():
    """
     johnson s baby -> johnsons baby
    """
    ...


def clean_cats():
    """
    "bebek bezi/bebek, oyuncak"

    """

    ...

def create_trees():
    cat_tree = defaultdict(set)
    brand_tree = defaultdict(set)

    original_brands = {}
    original_cats = {}

    def update(brands, subcats):

        clean_to_orig = {services.clean_name(b): b.lower() for b in brands}
        original_brands.update(clean_to_orig)
        brands = set(clean_to_orig.keys())

        clean_to_orig = {services.clean_name(c): c.lower() for c in subcats}
        original_cats.update(clean_to_orig)
        subcats = set(clean_to_orig.keys())

        for b in brands:
            brand_tree[b].update(subcats)

        for c in subcats:
            cat_tree[c].update(brands)

    ty_raw = services.read_json(input_dir / "ty_raw.json")
    for main_cat, filters in ty_raw.items():
        brands = filters.get("brand")
        subcats = filters.get("category")

        update(brands, subcats)

    watsons_raw = services.read_json(input_dir / "watsons_raw.json")
    for main_cat, filters in watsons_raw.items():
        brands = set(filters.get("marka"))
        subcats = set(filters.get("cats"))

        update(brands, subcats)

    pairs = services.read_json(input_dir / "brand_cat_pairs.json")
    for cat in pairs:
        brands = set(cat.get("brand"))
        subcats = set(cat.get("categories"))

        update(brands, subcats)

    brand_tree = {
        brand: [c for c in cats if c]
        for brand, cats in brand_tree.items()
        if len(brand) > 1
    }
    cat_tree = {
        cat: [c for c in brands if c]
        for cat, brands in cat_tree.items()
        if len(cat) > 1
    }

    services.save_json(input_dir / "cat_tree.json", cat_tree)

    services.save_json(input_dir / "original_cats.json", original_cats)


def create_brand_subcats_pairs(skus) -> tuple:
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
    add_from_skus(skus)
    return brand_subcats_pairs, clean_brand_original_brand_pairs


def create_subcat_brands_pairs() -> dict:
    ...


def add_clean_brands(sku):
    clean_brands = services.clean_list_of_strings(
        services.flatten(sku.get("brands", []))
    )
    sku[keys.CLEAN_BRANDS] = clean_brands
    return sku


def add_clean_cats(sku):
    cats = sku.get(keys.CATEGORIES, [])
    clean_cats = services.clean_list_of_strings(services.flatten(cats))
    sku[keys.CLEAN_CATS] = clean_cats
    return sku


def add_clean_sub_cats(sku):
    subcats = []
    for cat in sku.get(keys.CATEGORIES, []):
        if isinstance(cat, list):
            subcats.append(cat[-1])
        else:
            subcats.append(cat)

    subcats = [sub.split("/")[-1] for sub in subcats]
    clean_subcats = services.clean_list_of_strings(services.flatten(subcats))
    sku[keys.CLEAN_SUBCATS] = clean_subcats
    return sku


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


def get_clean_skus(full_skus):
    skus = get_skus_with_relevant_fields(full_skus)

    with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
        skus = pool.map(add_clean_brands, tqdm(skus))
        skus = pool.map(add_clean_cats, tqdm(skus))
        skus = pool.map(add_clean_sub_cats, tqdm(skus))

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


def get_brand_candidates(sku: dict, brand_pool: set) -> list:
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


def select_brand(brand_candidates: list) -> str:
    if brand_candidates:
        brand_candidates = list(set(brand_candidates))
        brand = sorted(brand_candidates, key=len)[-1]
        return brand


def summarize(skus):
    summary_keys = {"brand", "clean_names"}
    skus = [services.filter_keys(doc, summary_keys) for doc in skus]
    for doc in skus:
        doc["name"] = doc.pop("clean_names")[0]
    skus_with_brand = [sku for sku in skus if "brand" in sku]
    skus_without_brand = [sku for sku in skus if "brand" not in sku]
    services.save_json(output_dir / "skus_with_brand.json", skus_with_brand)
    services.save_json(output_dir / "skus_without_brand.json", skus_without_brand)


def add_brand_to_skus(full_skus, debug=False):
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
    skus = get_clean_skus(full_skus)

    # create and save brand subcat pairs
    brand_subcats_pairs, clean_brand_original_brand_pairs = create_brand_subcats_pairs(
        skus
    )
    if debug:
        services.save_json(output_dir / "brand_subcats_pairs.json", brand_subcats_pairs)
        services.save_json(
            output_dir / "clean_brand_original_brand_pairs.json",
            clean_brand_original_brand_pairs,
        )

    brand_pool = get_brand_pool(brand_subcats_pairs, skus)
    for sku in skus:
        brand_candidates = get_brand_candidates(sku, brand_pool)
        sku[keys.BRAND_CANDIDATES] = brand_candidates
        sku[keys.BRAND] = select_brand(brand_candidates)

    summarize(skus)


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)

    full_skus = services.read_json(input_dir / "full_skus.json")

    add_brand_to_skus(full_skus, debug=True)

    """
    brand tree logic is scattered, merge it

    """
