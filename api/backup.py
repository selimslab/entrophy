from data_services.mongo.collections import test_collection, items_collection, db
import api.sentry
from data_services import elastic
import services
from tqdm import tqdm

if __name__ == "__main__":
    # items_collection.aggregate([{"$match": {}}, {"$out": "docs_backup"}])
    products = [hit for hit in tqdm(elastic.scroll())]
    services.save_json("elastic_snapshot.json", products)
