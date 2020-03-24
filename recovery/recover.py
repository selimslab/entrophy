from tqdm import tqdm

import data_services.mongo.collections as collections
from data_services.elastic.main import Elastic
from services import json_util


def get_skus():
    cursor = collections.skus_collection.find({})
    skus = []
    for doc in tqdm(cursor):
        doc.pop("_id")
        skus.append(doc)
    return skus


def get_products():
    # cursor = collections.products_collection.find({})
    cursor = json_util.read_json("../oldfiles/products.json")
    products = []
    for doc in tqdm(cursor):
        if "_id" in doc:
            doc.pop("_id")
        products.append(doc)
    return products


def recover_firestore():
    skus = get_skus()
    firesync.batch_update_firestore(skus)


def reset_elastic():
    products = get_products()
    el = Elastic()

    # el.reset_index()

    el.update_docs(products)


def init_skus_collection():
    collections.skus_collection.delete_many({})
    batch = []
    for doc in tqdm(firesync.firestore_generator()):
        batch.append(doc)
        if len(batch) > 1000:
            collections.skus_collection.insert_many(batch)
            batch = []


def init_products_collection():
    collections.products_collection.delete_many({})
    el = Elastic()
    batch = []
    for hit in tqdm(el.scroll()):
        if hit:
            doc = hit.get("_source")
            doc["objectID"] = hit["_id"]
            batch.append(doc)
        if len(batch) > 1000:
            collections.products_collection.insert_many(batch)
            batch = []


if __name__ == "__main__":
    pass
