import data_services
from spec.model.sku import BasicSKU
from dataclasses import asdict
from data_services import elastic


def strip_debug_fields(skus):
    keys_to_sync = set(asdict(BasicSKU()).keys())
    fresh_skus = {
        sku_id: {
            k: v for k, v in sku.items()
            if k in keys_to_sync
        }
        for sku_id, sku in skus.items()
    }

    return fresh_skus


def sync_elastic(fresh_skus):
    old_skus = {
        hit.get("_id"): hit.get("_source")
        for hit in data_services.elastic.scroll()
    }

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
    print("ids_to_delete", len(ids_to_delete))

    elastic.replace_docs(to_be_added)
    elastic.replace_docs(to_be_updated)
    if ids_to_delete:
        elastic.delete_ids(ids_to_delete)


def sync_the_new_matching(skus):
    fresh_skus = strip_debug_fields(skus)
    sync_elastic(fresh_skus)
