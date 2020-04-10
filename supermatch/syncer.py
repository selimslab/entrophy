import data_services
from spec.model.sku import BasicSKU
from dataclasses import asdict
from data_services.elastic.main import Elastic


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

    ids_to_keep = set(fresh_skus.keys())
    old_ids = set(old_skus.keys())
    ids_to_delete = list(old_ids - ids_to_keep)

    to_be_added = list()
    to_be_updated = list()

    for doc_id, new_doc in fresh_skus.items():
        old_doc = old_skus.get(doc_id, {})

        if not old_doc:
            to_be_added.append(new_doc)
            continue

        if new_doc != old_doc:
            to_be_updated.append(new_doc)

    print("to_be_added", len(to_be_added))
    print("to_be_updated", len(to_be_updated))

    elastic = Elastic()
    elastic.update_docs(to_be_added)
    elastic.replace_docs(to_be_updated)
    if ids_to_delete:
        elastic.delete_ids(ids_to_delete)