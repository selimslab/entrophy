from collections import defaultdict
from typing import List
import services
import constants as keys


keys_to_merge = {
    keys.CATEGORIES,
    keys.SUB_CATEGORIES,
    keys.BRANDS_MULTIPLE,
    keys.CLEAN_NAMES,
    keys.CLEAN_COLORS,
    keys.CLEAN_CATS,
    keys.COLOR_PLURAL,
    keys.VARIANT_NAME,
}



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

    for pid, skus in groups.items():
        # merge info from multiple skus
        product = {keys.PRODUCT_ID: pid}
        for key in keys_to_merge:
            vals = [sku.get(key, []) for sku in skus]
            product[key] = services.flatten(vals)

        # subcats are treated specially, because every vendor has 1 vote for subcat for a product
        merged_subcats = defaultdict(list)
        for sku in skus:
            market_subs_pairs = sku.get(keys.SUB_CATEGORIES)
            for market, subs in market_subs_pairs.items():
                merged_subcats[market] += subs

        subs = [list(set(subs)) for subs in merged_subcats.values()]
        product[keys.SUB_CATEGORIES] = services.flatten(subs)

        products.append(product)

    return products
