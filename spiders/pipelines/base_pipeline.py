import constants as keys
import data_services.mongo.collections as collections
from data_services import MongoSync


class BasePipeline:
    def __init__(self, write_interval=None):
        if not write_interval:
            write_interval = 256
        self.mongo_sync = MongoSync(
            collection=collections.items_collection, write_interval=write_interval
        )

    @staticmethod
    def clean_item(item):
        return {
            k: v
            for k, v in dict(item).items()
            # a value can't be null or empty
            if v or v is False
        }

    @staticmethod
    def clean_promoted(item):
        if keys.PROMOTED in item:
            promoted = item.pop(keys.PROMOTED)
            for seller, link in promoted.items():
                seller_key = "promoted." + seller
                item[seller_key] = link
        return item

    def process_item(self, item, spider):
        return item

    def close_spider(self, spider):
        stats = spider.crawler.stats.get_stats()
        print("STATS", stats)
