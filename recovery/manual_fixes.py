from pprint import pprint

import constants as keys
import data_services.mongo.collections as collections


def ask(collection, query):
    cursor = collection.find(query)
    print(collection.count_documents(query))
    for doc in cursor[:10]:
        pprint(doc)


def unset():
    query = {}
    collections.items_collection.update_one(query, {"$unset": {keys.PROMOTED: 1}})
    ask(collections.items_collection, query)
    collections.items_collection.update_many(
        {keys.MARKET: keys.WATSONS}, {"$set": {keys.OUT_OF_STOCK: False}}
    )


"https://www.google.com/shopping/product/3973365335573817959"
