from pprint import pprint

import constants as keys
import data_services
import data_services.firebase.connect
import data_services.mongo.collections as collections
import data_services.elastic.query_elastic


def ask(collection, query):
    cursor = collection.find(query)
    print(collection.count_documents(query))
    for doc in cursor[:10]:
        pprint(doc)


def inspect_case(link):
    query = {keys.LINK: link}

    doc = collections.items_collection.find_one(query)
    pprint(doc)
    if not doc:
        return

    sku_id = doc.get(keys.SKU_ID)
    name = doc.get(keys.NAME)
    print(name, sku_id)
    data_services.elastic.query_elastic.search_elastic(name)




if __name__ == "__main__":
    pass
