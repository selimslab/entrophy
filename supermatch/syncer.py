import data_services
from spec.model.sku import BasicSKU
from dataclasses import asdict
from data_services import elastic
import data_services.firebase.connect as firebase_collections
import data_services.mongo.collections as mongo_collections


def strip_debug_fields(skus):
    keys_to_sync = set(asdict(BasicSKU()).keys())
    fresh_skus = {
        sku_id: {k: v for k, v in sku.items() if k in keys_to_sync}
        for sku_id, sku in skus.items()
    }
    return fresh_skus


def sync_datastores(to_be_updated, is_test=True):
    if is_test:
        index = "test"
        collection = firebase_collections.test_collection
        mongo_coll = mongo_collections.test_collection
    else:
        index = "products"
        collection = firebase_collections.skus_collection
        mongo_coll = mongo_collections.items_collection

    elastic.replace_docs(to_be_updated, index=index)
    data_services.batch_set_firestore(to_be_updated, collection=collection)
    data_services.sync_sku_ids(to_be_updated, mongo_coll)


def sync_updates(ids, fresh_skus, is_test):
    body = {"query": {"ids": {"values": ids}}}
    old_skus = {
        hit.get("_id"): hit.get("_source")
        for hit in data_services.elastic.scroll(body=body)
    }
    to_be_updated = list()
    for sku_id in ids:
        old_doc = old_skus.get(sku_id, {})
        new_doc = fresh_skus.get(sku_id, {})
        if old_doc and new_doc == old_doc:
            continue
        to_be_updated.append(new_doc)

    if to_be_updated:
        sync_datastores(to_be_updated, is_test)


def compare_and_sync(fresh_skus, is_test=True):
    ids_to_keep = set(fresh_skus.keys())
    print(len(ids_to_keep), "ids_to_keep")
    ids_to_delete = []
    if not is_test:
        body = {"stored_fields": []}
        all_ids = (hit.get("_id") for hit in data_services.elastic.scroll(body=body, duration="3m"))
        ids_to_delete = list(set(all_ids) - ids_to_keep)
        print(len(ids_to_delete), "ids_to_delete")

    batch_size = 1024

    ids = []
    for sku_id, new_doc in fresh_skus.items():
        ids.append(sku_id)
        if len(ids) > batch_size:
            sync_updates(ids, fresh_skus, is_test)
            ids = []

    sync_updates(ids, fresh_skus, is_test)

    if not is_test and ids_to_delete:
        elastic.delete_ids(ids_to_delete, index="products")
        # TODO why sync to fs?
        data_services.firestore_delete_by_ids(ids_to_delete, collection=firebase_collections.skus_collection)


def sync_the_new_matching(skus):
    fresh_skus = strip_debug_fields(skus)
    compare_and_sync(fresh_skus, is_test=False)


if __name__ == "__main__":
    pass
