import data_services
from spec.model.sku import BasicSKU
from dataclasses import asdict
from data_services import elastic
import data_services.firebase.connect as firebase_collections
import data_services.mongo.collections as mongo_collections
from data_services.mongo.mongo_sync import MongoSync
import logging


class Syncer:
    def __init__(self, is_test=None):
        if is_test is None:
            is_test = True

        self.is_test = is_test
        if self.is_test:
            logging.info("sync in test mode..")
            mongo_coll = mongo_collections.test_collection
            self.index = "test"
            self.fs_collection = firebase_collections.test_collection
            self.batch_size = 16
        else:
            mongo_coll = mongo_collections.items_collection
            self.index = "products"
            self.fs_collection = firebase_collections.skus_collection
            self.batch_size = 4096

        self.mongo_sync = MongoSync(collection=mongo_coll, write_interval=128)

    @staticmethod
    def strip_debug_fields(skus):
        keys_to_sync = set(asdict(BasicSKU()).keys())
        fresh_skus = {
            sku_id: {k: v for k, v in sku.items() if k in keys_to_sync}
            for sku_id, sku in skus.items()
        }
        return fresh_skus

    def sync_datastores(self, to_be_updated, all_doc_ids):
        elastic.replace_docs(to_be_updated, index=self.index)
        data_services.batch_set_firestore(to_be_updated, collection=self.fs_collection)
        data_services.sync_sku_ids(self.mongo_sync, to_be_updated, all_doc_ids)

    def create_updates(self, ids, skus):
        logging.info(f"ids, {ids}")
        body = {"query": {"ids": {"values": ids}}}

        old_skus = {
            hit.get("_id"): hit.get("_source")
            for hit in data_services.elastic.scroll(body=body, index=self.index)
        }
        to_be_updated = list()
        all_doc_ids = list()
        for sku_id in ids:
            old_sku = old_skus.get(sku_id, {})
            new_sku = skus.get(sku_id, {})
            doc_ids = new_sku.pop("doc_ids")
            if old_sku and new_sku == old_sku:
                continue
            to_be_updated.append(new_sku)
            doc_ids = [id for id in doc_ids if "clone" not in id]
            all_doc_ids.append(doc_ids)

        if to_be_updated:
            self.sync_datastores(to_be_updated, all_doc_ids)

    def compare_and_sync(self, skus):
        ids = []
        for sku_id, new_doc in skus.items():
            ids.append(sku_id)
            if len(ids) > self.batch_size:
                self.create_updates(ids, skus)
                ids = []

        if ids:
            self.create_updates(ids, skus)

        body = {"stored_fields": []}
        all_ids = [
            hit.get("_id")
            for hit in data_services.elastic.scroll(
                index=self.index, body=body, duration="10m"
            )
        ]

        ids_to_keep = set(skus.keys())
        print(len(ids_to_keep), "ids_to_keep")
        ids_to_delete = list(set(all_ids) - ids_to_keep)
        print(len(ids_to_delete), "ids_to_delete")

        print("all ids", all_ids)
        print("ids_to_keep", ids_to_keep)
        print("ids_to_delete", ids_to_delete)

        if ids_to_delete:
            elastic.delete_ids(ids_to_delete, index=self.index)
            data_services.firestore_delete_by_ids(
                ids_to_delete, collection=self.fs_collection
            )

    def sync_the_new_matching(self, skus):
        fresh_skus = self.strip_debug_fields(skus)
        self.compare_and_sync(fresh_skus)


if __name__ == "__main__":
    pass
