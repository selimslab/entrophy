from typing import Dict
from collections import defaultdict

import paths as paths
import services
import constants as keys

from cleaners.brand_to_clean import get_brand_original_to_clean
from cleaners.subcat_to_clean import get_subcat_original_to_clean


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


def create_indexes(products):
    brand_original_to_clean: dict = get_brand_original_to_clean(products)

    clean_brands = set(brand_original_to_clean.values())
    subcat_original_to_clean: dict = get_subcat_original_to_clean(
        products, clean_brands
    )

    possible_subcats_by_brand: dict = get_possible_subcats_by_brand(
        products, brand_original_to_clean, subcat_original_to_clean
    )

    services.save_json(paths.brand_original_to_clean, brand_original_to_clean)
    services.save_json(paths.subcat_original_to_clean, subcat_original_to_clean)
    services.save_json(
        paths.output_dir / "possible_subcats_by_brand.json", possible_subcats_by_brand
    )

    return brand_original_to_clean, subcat_original_to_clean, possible_subcats_by_brand
