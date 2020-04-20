from data_services.firebase.connect import test_collection, skus_collection
from data_services.elastic.query_elastic import search_by_ids

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


if __name__ == "__main__":
    pass
