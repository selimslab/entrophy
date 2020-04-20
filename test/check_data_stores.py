from data_services.firebase.connect import test_collection

from data_services.mongo.collections import items_collection
from bson import ObjectId


def check_firestore():
    # print(test_collection.document("test").get().to_dict())
    docs = test_collection.stream()
    for doc in docs:
        print(u"{} => {}".format(doc.id, doc.to_dict()))


def check_mongo():
    link = "5d8086d74a4834d16139f82e+clone016"
    doc = items_collection.find_one({"link": link})

    print(doc)


if __name__ == "__main__":
    check_mongo()
