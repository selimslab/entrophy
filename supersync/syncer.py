import data_services
from supersync import doc_comparator
from spec.model.sku import BasicSKU
from dataclasses import asdict


def strip_debug_fields(skus):
    keys_to_sync = set(asdict(BasicSKU()).keys())
    fresh_skus = [
        {k: v for k, v in sku.items()
         if k in keys_to_sync
         }
        for sku in skus
    ]

    return fresh_skus


def sync_the_new_matching(fresh_skus):
    old_skus = data_services.get_id_product_pairs()
    updates = doc_comparator.compare_docs(
        fresh_skus, old_skus
    )
    data_services.sync_elastic(updates)
