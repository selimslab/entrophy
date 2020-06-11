from collections import defaultdict, Counter
import logging
from typing import List

import services
import constants as keys
from paths import input_dir, output_dir

from preprocess import filter_docs, group_products
from original_to_clean import get_brand_original_to_clean, get_subcat_original_to_clean
from freq import get_brand_freq, get_subcat_freq
from branding import get_brand_pool, get_brand_candidates, select_brand
from subcats import (
    cat_to_subcats,
    get_possible_subcats_for_this_product,
    get_subcat_candidates,
    select_subcat
)


def get_possible_subcats_by_brand(
        products, brand_original_to_clean, subcat_original_to_clean
):
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
    subcat_freq = get_subcat_freq(products, subcat_original_to_clean)
    possible_subcats_by_brand = get_possible_subcats_by_brand(
        products, brand_original_to_clean, subcat_original_to_clean
    )

    brand_pool = get_brand_pool(products, possible_subcats_by_brand)
    services.save_json(output_dir / "brand_pool.json", sorted(list(brand_pool)))

    # add brand
    for product in products:
        brand_candidates = get_brand_candidates(product, brand_pool)
        product[keys.BRAND_CANDIDATES] = dict(Counter(brand_candidates))

        the_most_frequent_brand = select_brand(brand_candidates, brand_freq)
        product[keys.BRAND] = the_most_frequent_brand

    # add subcat
    for product in products:
        possible_subcats_for_this_product = get_possible_subcats_for_this_product(
            product, possible_subcats_by_brand, subcat_original_to_clean
        )
        subcat_candidates = get_subcat_candidates(
            product, possible_subcats_for_this_product
        )
        if subcat_candidates:
            product[keys.SUBCAT_CANDIDATES] = dict(Counter(subcat_candidates))
            product[keys.SUBCAT] = select_subcat(subcat_candidates, subcat_freq)


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)
    brand_subcats_pairs_path = output_dir / "brand_subcats_pairs.json"
    skus = services.read_json(input_dir / "skus.json")
    refresh(skus)
    print("done!")
