from bson import ObjectId
import constants as keys
import data_services.mongo.collections as collections
from data_services.mongo.mongo_sync import MongoSync


def get_in_stock(market):
    return collections.items_collection.count_documents(
        {keys.MARKET: market, keys.OUT_OF_STOCK: {"$ne": True}}
    )


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
        selector = {"_id": ObjectId(doc_id)}
        command = {"$set": updates}
        mongosync.add_update(selector, command)
    mongosync.bulk_exec()
