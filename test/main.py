from pprint import pprint

import constants as keys
import data_services
import data_services.firebase.main
import data_services.mongo.collections as collections
import data_services.query_elastic


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
    product_id = doc.get(keys.PRODUCT_ID)
    name = doc.get(keys.NAME)

    print(name, sku_id, product_id)

    print("PRODUCT")
    data_services.query_elastic.search_elastic(name)

    print("SKU")
    data_services.firebase.main.search_in_firestore(sku_id)

    if product_id:
        data_services.query_elastic.search_elastic_by_ids([product_id])
        ask(collections.products_collection, {keys.objectID: product_id})


def get_links_of_a_product(product_id):
    links = collections.items_collection.find(
        {keys.objectID: product_id}, {"_id": 0, keys.LINK: 1}
    )
    links = list(links)
    pprint(links)
    return links


if __name__ == "__main__":
    pass
