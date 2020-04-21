import data_services.mongo.collections as mongo_collections
from data_services.mongo.mongo_sync import MongoSync
import api.sentry
from data_services import elastic
import services
from tqdm import tqdm
import collections


def backup_elastic():
    mongo_sync = MongoSync(collection=mongo_collections.products_backup)
    for hit in tqdm(elastic.scroll()):
        doc = hit.get("_source")
        selector = {"_id": hit.get("_id")}
        mongo_sync.add_update_one(selector, doc)
    mongo_sync.bulk_exec()


def backup_raw_items():
    mongo_collections.items_collection.aggregate([{"$match": {}}, {"$out": "docs_backup"}])


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

if __name__ == "__main__":
    backup_raw_items()

