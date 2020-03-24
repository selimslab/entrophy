import random


def create_product_id(skus: list, sku_ids: list, used_product_ids: set) -> str:
    """
    use the most common PRODUCT_ID if present, else choose the ->strfirst sorted

    product id will be unique because sku_ids are unique
    """
    ids_count = [sku.get("product_ids_count", {}) for sku in skus]
    merged_count = dict()
    for id_count in ids_count:
        for id, count in id_count.items():
            if id and id not in used_product_ids:
                merged_count[id] = merged_count.get(id, 0) + count

    if merged_count:
        product_id = max(merged_count, key=merged_count.get)

    else:
        candidate_ids = [
            sku_id
            for sku_id in sku_ids
            if sku_id not in used_product_ids and "clone" not in sku_id
        ]
        if candidate_ids:
            product_id = sorted(candidate_ids)[0]
        else:
            product_id = sorted(sku_ids)[0] + str(random.randint(1, 100))
            while product_id in used_product_ids:
                product_id = sorted(sku_ids)[0] + str(random.randint(1, 100))

    return product_id
