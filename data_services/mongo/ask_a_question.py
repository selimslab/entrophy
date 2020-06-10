import constants as keys
from data_services.mongo.collections import items_collection
from pprint import pprint


def ask_a_question():
    print(items_collection.count_documents({"color": {"$exists": True}}))
    cursor = {}
    for doc in cursor:
        pprint(doc)


if __name__ == "__main__":
    ask_a_question()
