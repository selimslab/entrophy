from bson import ObjectId
import constants as keys
import data_services.mongo.collections as collections
from data_services.elastic.main import Elastic
from data_services.mongo.mongo_sync import MongoSync
from tqdm import tqdm

from data_services.query_elastic import search_elastic_by_ids


def get_sku_ids_by_links(links):
    return collections.items_collection.find(
        {
            keys.LINK: {"$exists": True, "$in": links},
        },
        {"_id": 0, keys.LINK: 1, keys.SKU_ID: 1},
    )


def sync_mongo(collection, item_updates):
    to_be_added, to_be_updated, ids_to_delete = item_updates
    mongosync = MongoSync(collection)
    mongosync.batch_insert(to_be_added)
    mongosync.batch_update_mongo(to_be_updated)
    if ids_to_delete:
        collection.delete_many({"objectID": {"$in": ids_to_delete}})


def sync_sku_and_product_ids(id_tree):
    mongosync = MongoSync(collections.items_collection, write_interval=64000)
    for doc_id, updates in id_tree.items():
        if "+clone" in doc_id:
            # skip cloned docs
            continue
        selector = {"_id": ObjectId(doc_id)}
        command = {"$set": updates}
        mongosync.add_update(selector, command)
    mongosync.bulk_exec()


if __name__ == "__main__":
    search_elastic_by_ids(["5e54cfc2d1e09b159549e7e3", "5e11bd9c1b07cf6bf3b913dd", "5d7bdfa6525e36c343df0d8c",
                           "5d7bdfa6525e36c343df0e4e"])
