from paths import *
from prepare_docs_to_guess import *
from guess import *
from index import get_brand_index, get_cat_index
from count_fields import stat
import multiprocessing
from collections import Counter


def add_brand(sku):
    """
    find brand first,
    there only a few possible cats for this brand
    indexes should reflect that too

    johnson s baby -> johnsons baby
    """
    candidates = sku.get("clean_brands", [])
    clean_names = sku.get("clean_names", [])

    for name in clean_names:
        for brand in brands:
            if brand in name:
                candidates.append(brand)

    if candidates:
        candidates = list(set(candidates))
        brand = sorted(candidates, key=len)[-1]
        sku["brand"] = brand

    return sku


def add_cat():
    pass


def clean_sku(sku):
    cats = sku.get(keys.CATEGORIES, [])
    clean_cats = services.clean_list_of_strings(services.flatten(cats))

    subcats = []
    for cat in cats:
        if isinstance(cat, list):
            subcats.append(cat[-1])
        else:
            subcats.append(cat)

    subcats = [sub.split("/")[-1] for sub in subcats]
    clean_subcats = services.clean_list_of_strings(services.flatten(subcats))

    clean_brands = services.clean_list_of_strings(services.flatten(sku.get("brands", [])))

    sku.update(
        {
            "clean_brands": clean_brands,
            "clean_cats": clean_cats,
            "clean_subcats": clean_subcats,
        }
    )

    return sku


def prep():
    full_skus = services.read_json(input_dir / "full_skus.json")

    relevant_keys = {
        keys.CATEGORIES,
        "brands",
        "clean_names"
    }
    skus = [services.filter_keys(doc, relevant_keys) for doc in full_skus.values()]

    with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
        skus = pool.map(clean_sku, tqdm(skus))

    with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
        skus_with_brand = pool.map(add_brand, tqdm(skus))

    summary_keys = {
        "brand",
        "clean_names"
    }
    skus = [services.filter_keys(doc, summary_keys)
            for doc in skus_with_brand]

    for doc in skus:
        doc["name"] = doc.pop("clean_names")[0]

    skus_with_brand = [sku for sku in skus if "brand" in sku]
    skus_without_brand = [sku for sku in skus if "brand" not in sku]

    services.save_json(
        output_dir / "skus_with_brand.json",
        skus_with_brand)
    services.save_json(
        output_dir / "skus_without_brand.json",
        skus_without_brand)
    # cat_tree = services.read_json(input_dir / "cat_tree.json")


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)

    brand_tree = services.read_json(input_dir / "brand_tree.json")
    brands = set(brand_tree.keys())
    first_token_freq = services.read_json(input_dir / "first_token_freq.json")

    brands.update(set(first_token_freq.keys()))
    prep()
