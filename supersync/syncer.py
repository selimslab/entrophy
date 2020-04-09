import data_services
from supersync import doc_comparator
from spec.model.sku import BasicSKU
from dataclasses import asdict


def sync_the_new_matching(skus):
    if not skus:
        raise AttributeError("no matching_collection")

    keys_to_sync = set(asdict(BasicSKU()).keys())

    skus_to_sync = [
        {k: v for k, v in sku.items()
         if k in keys_to_sync
         }
        for _, sku in skus.items()
    ]
    old_skus = data_services.get_id_product_pairs()
    updates = doc_comparator.compare_docs(
        skus_to_sync, old_skus
    )

    data_services.sync_elastic(updates)
