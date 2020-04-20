import constants as keys
import data_services.mongo.collections as collections
from data_services.mongo.mongo_sync import MongoSync
from bson import ObjectId


def get_in_stock(market):
    return collections.items_collection.count_documents(
        {keys.MARKET: market, keys.OUT_OF_STOCK: {"$ne": True}}
    )


def get_sku_ids_by_links(links):
    return collections.items_collection.find(
        {keys.LINK: {"$exists": True, "$in": links}},
        {"_id": 0, keys.LINK: 1, keys.SKU_ID: 1},
    )


def sync_mongo(collection, item_updates):
    to_be_added, to_be_updated, ids_to_delete = item_updates
    mongosync = MongoSync(collection)
    mongosync.batch_insert(to_be_added)
    mongosync.batch_update_mongo(to_be_updated)
    if ids_to_delete:
        collection.delete_many({"objectID": {"$in": ids_to_delete}})


def sync_sku_ids(mongo_sync, skus, all_doc_ids):
    for sku, doc_ids in zip(skus, all_doc_ids):
        doc_ids = [ObjectId(id) for id in doc_ids]
        for id in doc_ids:
            # selector = {"_id": {"$in": doc_ids}}
            selector = {"_id": id}
            update = {keys.SKU_ID: sku.get(keys.SKU_ID)}
            command = {"$set": update}
            mongo_sync.add_update_one(selector, command)
    mongo_sync.bulk_exec()


def test():
    doc_ids = ["5df35a775bc9b8611f193757", "5df35ad05bc9b8611f1a0289"]
    mongo_sync = MongoSync(collection=collections.test_collection)
    doc_ids = [ObjectId(id) for id in doc_ids]
    selector = {"_id": {"$in": doc_ids}}
    update = {"x": "ok"}
    command = {"$set": update}
    mongo_sync.add_update_one(selector, command)
    print(mongo_sync.ops)
    mongo_sync.bulk_exec()

    for doc in mongo_sync.collection.find({"_id": {"$in": doc_ids}}):
        print(doc)


if __name__ == "__main__":
    test()
