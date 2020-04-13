from data_services.firebase.connect import test_collection

from data_services.mongo.collections import items_collection
from bson import ObjectId


def check_firestore():
    # print(test_collection.document("test").get().to_dict())
    docs = test_collection.stream()
    for doc in docs:
        print(u"{} => {}".format(doc.id, doc.to_dict()))


print(items_collection.find_one({"_id": {"$in": [ObjectId("5d7be09143a5a28ff82323f7")]}}))
