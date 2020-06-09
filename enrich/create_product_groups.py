from collections import defaultdict
from typing import List

import services

import constants as keys


def create_product_groups(skus: dict) -> List[dict]:
    relevant_keys = {
        keys.CATEGORIES,
        keys.BRANDS_MULTIPLE,
        keys.CLEAN_NAMES,
        keys.SKU_ID,
        keys.PRODUCT_ID,
    }

    groups = defaultdict(list)
    products = []
    for sku_id, sku in skus.items():
        sku = services.filter_keys(sku, relevant_keys)
        if keys.PRODUCT_ID in sku:
            pid = sku.get(keys.PRODUCT_ID)
            groups[pid].append(sku)
        else:
            products.append(sku)

    for pid, docs in groups.items():
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


if __name__ == "__main__":
    ...
