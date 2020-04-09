import constants as keys
from services import flattener


def create_id_tree(sku_id_doc_ids_pairs, products):
    id_tree = {}

    for sku_id, doc_ids in sku_id_doc_ids_pairs.items():
        for doc_id in doc_ids:
            doc = id_tree.get(doc_id, {})
            doc[keys.SKU_ID] = sku_id
            doc[keys.PRODUCT_ID] = sku_id
            id_tree[doc_id] = doc

    for p in products:
        product_id = p.get(keys.objectID)
        if not product_id:
            print("no pid", p)
        if product_id and keys.VARIANTS in p:
            sku_ids = p.get(keys.VARIANTS, [])
            doc_ids = [sku_id_doc_ids_pairs.get(sku_id) for sku_id in sku_ids]
            doc_ids = flattener.flatten(doc_ids)
            for doc_id in doc_ids:
                doc = id_tree.get(doc_id, {})
                doc[keys.PRODUCT_ID] = product_id
                id_tree[doc_id] = doc

    return id_tree
