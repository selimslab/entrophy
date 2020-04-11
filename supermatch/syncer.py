import data_services
from spec.model.sku import BasicSKU
from dataclasses import asdict
from data_services import elastic
from data_services.firebase.connect import skus_collection


def strip_debug_fields(skus):
    keys_to_sync = set(asdict(BasicSKU()).keys())
    fresh_skus = {
        sku_id: {k: v for k, v in sku.items() if k in keys_to_sync}
        for sku_id, sku in skus.items()

    }

    return fresh_skus


def get_updates(ids, fresh_skus):
    body = {"query": {"ids": {"values": ids}}}
    old_skus = {
        hit.get("_id"): hit.get("_source") for hit in data_services.elastic.scroll(body=body)
    }

    to_be_updated = list()

    for sku_id in ids:
        old_doc = old_skus.get(sku_id, {})
        new_doc = fresh_skus.get(sku_id, {})

        if old_doc and new_doc == old_doc:
            continue
        to_be_updated.append(new_doc)

    ids_seen = set(old_skus.keys())
    return to_be_updated, ids_seen


def compare_and_sync(fresh_skus):
    ids_to_keep = set(fresh_skus.keys())
    old_ids = set()

    batch_size = 1024

    ids = []
    for sku_id, new_doc in fresh_skus.items():
        ids.append(sku_id)
        if len(ids) > batch_size:
            to_be_updated, ids_seen = get_updates(ids, fresh_skus)
            old_ids.update(ids_seen)
            sync_datastores(to_be_updated)
            ids = []

    ids_to_delete = list(old_ids - ids_to_keep)
    if ids_to_delete:
        elastic.delete_ids(ids_to_delete, index="products")
        # data_services.firestore_delete_by_ids(ids_to_delete, collection=skus_collection)


def sync_datastores(to_be_updated):
    elastic.replace_docs(to_be_updated, index="products")
    data_services.batch_set_firestore(to_be_updated, collection=skus_collection)
    data_services.mongo_sync_sku_ids(to_be_updated)


def sync_the_new_matching(skus):
    fresh_skus = strip_debug_fields(skus)
    compare_and_sync(fresh_skus)
