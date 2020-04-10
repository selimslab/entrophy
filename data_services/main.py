from bson import ObjectId
import constants as keys
import data_services.firebase.main as fire_sync
import data_services.mongo.collections as collections
from data_services.elastic.main import Elastic
from data_services.mongo.mongo_sync import MongoSync
import services
from tqdm import tqdm


def sync_firestore(updates):
    print("syncing skus..")
    to_be_added, to_be_updated, ids_to_delete = updates
    fire_sync.batch_update_firestore(to_be_added)
    fire_sync.batch_update_firestore(to_be_updated)
    if ids_to_delete:
        fire_sync.delete_old_ids(ids_to_delete)


def update_elastic_docs(docs):
    el = Elastic()
    el.update_docs(docs)


def search_elastic_by_ids(ids: list) -> list:
    el = Elastic()
    # body = {"query": {"ids": {"values": ids}}}
    body = {
        "_source": {
            "includes": ["prices"]
        },
        "query": {"ids": {"values": ids}}
    }
    return el.search(body)


def search_elastic(query):
    el = Elastic()

    body = {
        "query": {
            "bool": {
                "must": {
                    "multi_match": {
                        "query": query,
                        "fields": ["name^2", "tags"],
                        "fuzziness": "AUTO",
                        "operator": "and",
                    }
                },
            }
        },
        "sort": ["_score"],
    }
    return el.search(body)


def search_barcode(barcodes: list):
    el = Elastic()

    body = {
        "query": {
            "bool": {
                "must": [{"match_all": {}}, ],
                "filter": [{"terms": {"barcodes": barcodes, }}, ],
            }
        }
    }

    return el.search(body)


def get_id_product_pairs():
    el = Elastic()

    pairs = dict()
    for hit in tqdm(el.scroll()):
        doc = hit.get("_source")
        product_id = hit.get("_id")
        doc[keys.objectID] = product_id
        pairs[product_id] = doc

    return pairs


def search_in_firestore(doc_id):
    # fs.batch_update_firestore([test])
    doc_ref = fire_sync.firestore_client.collection("skus").document(doc_id)
    doc = doc_ref.get()
    print(doc.to_dict())


def get_docs_to_match(query: dict):
    projection = {
        "_id": 1,
        keys.NAME: 1,
        keys.SRC: 1,
        keys.MARKET: 1,
        keys.PRICE: 1,
        keys.DIGITS: 1,
        keys.UNIT: 1,
        keys.SIZE: 1,
        keys.OUT_OF_STOCK: 1,
        keys.LINK: 1,
        keys.BARCODES: 1,
        keys.PROMOTED: 1,
        keys.VARIANTS: 1,
        keys.VARIANT_NAME: 1,
        keys.SKU_ID: 1,
        keys.PRODUCT_ID: 1,
    }
    cursor = collections.items_collection.find(query, projection)
    return cursor


def sync_mongo(collection, item_updates):
    to_be_added, to_be_updated, ids_to_delete = item_updates
    mongosync = MongoSync(collection)
    mongosync.batch_insert(to_be_added)
    mongosync.batch_update_mongo(to_be_updated)
    if ids_to_delete:
        collection.delete_many({"objectID": {"$in": ids_to_delete}})


def sync_sku_and_product_ids(id_tree):
    mongosync = MongoSync(collections.items_collection, write_interval=64000)
    for doc_id, updates in id_tree.items():
        if "+clone" in doc_id:
            # skip cloned docs
            continue
        selector = {"_id": ObjectId(doc_id)}
        command = {"$set": updates}
        mongosync.add_update(selector, command)
    mongosync.bulk_exec()


def get_google_variants():
    return collections.items_collection.distinct(
        keys.VARIANTS, {keys.MARKET: keys.GOOGLE}
    )


def get_gratis_product_names(product_links: set):
    cursor = collections.items_collection.find(
        {keys.MARKET: keys.GRATIS, keys.LINK: {"$in": list(product_links)}},
        {keys.LINK: 1, keys.NAME: 1},
    )
    gratis_product_names = dict()
    for doc in cursor:
        gratis_product_names[doc.get(keys.LINK)] = doc.get(keys.NAME)

    return gratis_product_names


def get_links_of_products() -> set:
    links = collections.items_collection.distinct(keys.LINK, {keys.MARKET: keys.GRATIS})
    clean_links = (link[:-1] if link[-1] == "/" else link for link in links)
    product_links = (link.split("?")[0] for link in clean_links if "?sku" in link)
    links_of_products = (
        link for link in product_links if not link.split("/")[-1].isdigit()
    )

    return set(links_of_products)


if __name__ == "__main__":
    search_elastic_by_ids(["5e54cfc2d1e09b159549e7e3", "5e11bd9c1b07cf6bf3b913dd", "5d7bdfa6525e36c343df0d8c",
                           "5d7bdfa6525e36c343df0e4e"])
