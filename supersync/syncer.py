import data_services
from supersync import doc_comparator


def sync_the_new_matching(skus):
    if not skus:
        raise AttributeError("no matching_collection")

    id_product_pairs = data_services.get_id_product_pairs()
    product_updates = doc_comparator.compare_docs(
        matching_collection.products, id_product_pairs
    )

    data_services.sync_products_to_elastic(product_updates)

    data_services.sync_sku_and_product_ids(matching_collection.id_tree)

    id_sku_pairs = data_services.get_id_sku_pairs(id_product_pairs)
    sku_updates = doc_comparator.compare_docs(matching_collection.skus, id_sku_pairs)
    data_services.sync_skus_to_firestore(sku_updates)
