import data_services.mongo.collections as mongo_collections
from data_services.mongo.mongo_sync import MongoSync
from data_services import elastic
import services
from tqdm import tqdm
import collections
import sentry_sdk
from data_services.mongo.connect import db, newdb
import logging

sentry_sdk.init("https://39fd5a66307d47dcb3e9c37a8b709c44@sentry.io/5186400")


def backup_elastic():
    mongo_sync = MongoSync(collection=mongo_collections.products_backup)
    for hit in tqdm(elastic.scroll()):
        doc = hit.get("_source")
        selector = {"_id": hit.get("_id")}
        mongo_sync.add_update_one(selector, doc)
    mongo_sync.bulk_exec()


def backup_raw_items():
    mongo_collections.items_collection.aggregate(
        [{"$match": {}}, {"$out": "docs_backup"}]
    )


def inspect_prods():
    prods = services.read_json("elastic_snapshot.json")

    pairs = collections.defaultdict(list)

    for hit in tqdm(prods):
        doc = hit.get("_source")
        id = hit.get("_id")
        links = services.flatten(doc.get("links", []))
        for link in links:
            pairs[link] += [id]

    pairs = {link: ids for link, ids in pairs.items() if len(set(ids)) > 1}

    services.save_json("links.json", pairs)


def migrate_mongo():
    from spec.model.doc import BaseDoc
    from dataclasses import asdict
    batch = []
    basekeys = set(asdict(BaseDoc()).keys())
    basekeys.add("_id")
    print(basekeys)
    for doc in tqdm(db["items"].find({})):
        doc = {k: v for k, v in doc.items() if k in basekeys}
        batch.append(doc)
        if len(batch) > 300:
            newdb["raw_products"].insert_many(batch)
            batch = []

    if batch:
        newdb["raw_products"].insert_many(batch)


if __name__ == "__main__":
    migrate_mongo()
