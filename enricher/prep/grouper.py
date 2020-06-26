from collections import defaultdict
from typing import List
import services
import constants as keys

keys_to_merge = {
    keys.CATEGORIES,
    keys.SUB_CATEGORIES,
    keys.BRANDS_MULTIPLE,
    keys.CLEAN_NAMES,
    keys.CLEAN_CATS,
    keys.COLOR,
    keys.VARIANT_NAME,
}

relevant_keys = {keys.SKU_ID, keys.PRODUCT_ID}

relevant_keys.update(keys_to_merge)


def filter_docs(docs: List[dict]) -> List[dict]:
    """ only relevant_keys can stay """
    return [services.filter_keys(doc, relevant_keys) for doc in docs]


def group_products(filtered_skus: List[dict]) -> List[dict]:
    """ group skus to products
    there will be 2 kind of docs, product members and singles
    [
    {pid } -> product member
    {sku_id}
    ]

    """
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
        product = {keys.PRODUCT_ID: pid}
        for key in keys_to_merge:
            vals = [doc.get(key, []) for doc in docs]
            product[key] = services.flatten(vals)

        products.append(product)

    return products
