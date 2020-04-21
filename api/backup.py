from data_services.mongo.collections import test_collection, items_collection, db
import api.sentry


if __name__ == "__main__":
    items_collection.aggregate([{"$match": {}}, {"$out": "docs_backup"}])
