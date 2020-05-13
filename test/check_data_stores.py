from data_services.firebase.connect import test_collection, skus_collection
from data_services.elastic.query_elastic import search_by_ids, search_elastic

from data_services.mongo.collections import items_collection
from bson import ObjectId
from pprint import pprint
import constants as keys
import services


def check_firestore():
    # print(test_collection.document("test").get().to_dict())
    docs = test_collection.stream()
    for doc in docs:
        print(u"{} => {}".format(doc.id, doc.to_dict()))


def search_fs_by_object_ids(ids):
    docs = skus_collection.where("objectID", "in", ids).stream()
    for doc in docs:
        pprint(doc.to_dict())


def check_mongo():
    link = "5d8086d74a4834d16139f82e+clone016"
    doc = items_collection.find_one({"link": link})

    print(doc)


def ask(collection, query):
    cursor = collection.find(query)
    print(collection.count_documents(query))
    for doc in cursor[:10]:
        pprint(doc)


def inspect_case(link):
    query = {keys.LINK: link}

    doc = items_collection.find_one(query)
    pprint(doc)
    if not doc:
        return

    sku_id = doc.get(keys.SKU_ID)
    name = doc.get(keys.NAME)
    print(name, sku_id)
    search_elastic(name)


def foo(d, l):
    d[3][2] = 8
    l.append(5)


def bar():
    d = {3: {2: 4}}
    l = []
    foo(d, l)
    print(d, l)


def brand():
    pro = {"_id": 0, keys.LINK: 1, keys.SKU_ID: 1}

    count = items_collection.count_documents(
        {keys.MARKET: "ty", keys.BARCODES: {"$exists": True}},
    )
    print(count)


if __name__ == "__main__":
    brand()
