from pprint import pprint

import constants as keys
import data_services.mongo.collections as collections
from data_services import MongoSync
from data_services.mongo.connect import db


def ask(collection, query):
    cursor = collection.find(query)
    print(collection.count_documents(query))
    for doc in cursor:
        pprint(doc)


def manual_test_add_to_set():
    col = collections.test_collection

    mongo_sync = MongoSync(collection=col, write_interval=1)
    selector = {keys.LINK: "EMPTY"}
    ask(col, selector)

    command = {"$addToSet": {"barcodes": {"$each": []}}, "$set": {"name": "TEST"}}

    mongo_sync.add_update(selector, command)

    ask(col, selector)


def show_collection_info(collection):
    print(db.collection_names())

    print(
        collection.list_indexes(), collection.find({}).count(),
    )


def manual_test_dot_notation():
    col = collections.test_collection

    mongo_sync = MongoSync(collection=col, write_interval=1)
    selector = {keys.LINK: "EMPTY"}
    ask(col, selector)

    command = {"$set": {"prices.3,14": "TEST"}}

    mongo_sync.add_update(selector, command)

    ask(col, selector)


if __name__ == "__main__":
    pass
