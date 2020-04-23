import data_services.mongo.collections as mongo_collections
from data_services.mongo.mongo_sync import MongoSync
from data_services import elastic
from tqdm import tqdm
import sentry_sdk

sentry_sdk.init("https://39fd5a66307d47dcb3e9c37a8b709c44@sentry.io/5186400")


def backup_elastic():
    mongo_sync = MongoSync(collection=mongo_collections.elastic_backup)
    for hit in tqdm(elastic.scroll()):
        doc = hit.get("_source")
        selector = {"_id": hit.get("_id")}
        mongo_sync.add_update_one(selector, doc)
    mongo_sync.bulk_exec()


def backup_raw_items():
    mongo_collections.items_collection.aggregate(
        [{"$match": {}}, {"$out": "raw_products_backup"}]
    )


if __name__ == "__main__":
    backup_raw_items()
