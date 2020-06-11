from collections import defaultdict, Counter
import logging
from typing import List

import services
import constants as keys
from paths import input_dir, output_dir

from subcat import cat_to_subcats


def filter_docs(docs):
    relevant_keys = {
        keys.CATEGORIES,
        keys.BRANDS_MULTIPLE,
        keys.CLEAN_NAMES,
        keys.SKU_ID,
        keys.PRODUCT_ID,
    }
    return [services.filter_keys(doc, relevant_keys) for doc in docs]


def get_brand_original_to_clean(products: List[dict]):
    logging.info("cleaning brands..")
    brand_original_to_clean = {}

    for product in products:
        brands = product.get(keys.BRANDS_MULTIPLE, [])
        for brand in brands:
            if brand not in brand_original_to_clean:
                brand_original_to_clean[brand] = services.clean_string(brand)

    return brand_original_to_clean


def get_subcat_original_to_clean(products: List[dict]):
    logging.info("cleaning subcats..")
    subcat_original_to_clean = {}
    for product in products:
        subcats = product.get(keys.SUB_CATEGORIES, [])
        for sub in subcats:
            if sub not in subcat_original_to_clean:
                subcat_original_to_clean[sub] = services.clean_string(sub)
    return subcat_original_to_clean


def group_products(filtered_skus: List[dict]) -> List[dict]:
    groups = defaultdict(list)
    products = []
    for sku in filtered_skus:
        if keys.PRODUCT_ID in sku:
            pid = sku.get(keys.PRODUCT_ID)
            groups[pid].append(sku)
        else:
            products.append(sku)

    for pid, docs in groups.items():
        # merge info from multiple skus
        brands = [doc.get(keys.BRANDS_MULTIPLE) for doc in docs]
        cats = [doc.get(keys.CATEGORIES) for doc in docs]
        clean_names = [doc.get(keys.CLEAN_NAMES) for doc in docs]

        product = {
            keys.PRODUCT_ID: pid,
            keys.BRANDS_MULTIPLE: services.flatten(brands),
            keys.CATEGORIES: services.flatten(cats),
            keys.CLEAN_NAMES: services.flatten(clean_names),
        }
        products.append(product)

    return products


def get_brand_freq(products, brand_original_to_clean):
    """  how many items has been given this  brand by a vendor

    "erikli": 89,
    "damla": 13,
    "torku": 929

    """
    brand_freq = Counter()

    for product in products:
        brands = product.get(keys.BRANDS_MULTIPLE, [])
        clean_brands = [brand_original_to_clean.get(b) for b in brands]
        brand_freq.update(clean_brands)

    return brand_freq


def get_subcat_freq(products, subcat_original_to_clean):
    """  how many items has been given this subcat by a vendor """

    subcat_freq = Counter()

    for product in products:
        subcats = product.get(keys.SUB_CATEGORIES, [])
        clean_subcats = [subcat_original_to_clean.get(s) for s in subcats]
        subcat_freq.update(clean_subcats)

    return subcat_freq


def get_possible_subcats_by_brand(products, brand_original_to_clean, subcat_original_to_clean):
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
            possible_subcats_by_brand[clean_brand].add(set(clean_subcats))

    return possible_subcats_by_brand


def refresh(skus):
    """
    run the data enrichment from scratch

    next: use sku_ids, will be needed to use with supermatch

    with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
    """
    filtered_skus = filter_docs(skus)
    products = group_products(filtered_skus)

    # derive_subcats_from_product_cats
    for product in products:
        cats = product.get(keys.CATEGORIES, [])
        subcat_lists = [cat_to_subcats(cat) for cat in cats]
        product[keys.SUB_CATEGORIES] = services.flatten(subcat_lists)

    # Dr O'etker -> dr oetker
    brand_original_to_clean = get_brand_original_to_clean(products)
    subcat_original_to_clean = get_subcat_original_to_clean(products)

    brand_freq = get_brand_freq(products, brand_original_to_clean)
    subcat_freq = get_brand_freq(products, subcat_original_to_clean)
    possible_subcats_by_brand = get_possible_subcats_by_brand(products,
                                                              brand_original_to_clean,
                                                              subcat_original_to_clean)


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)
    brand_subcats_pairs_path = output_dir / "brand_subcats_pairs.json"
    skus = services.read_json(input_dir / "skus.json")
    refresh(skus)
    print("done!")
