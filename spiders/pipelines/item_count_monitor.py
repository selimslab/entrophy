import constants as keys

import data_services.mongo.collections as collections
from services import send_email


class ItemCountMonitor:
    def check_for_anomalies(self, spider_name, stats):
        existing_item_count = collections.items_collection.count_documents(
            {keys.MARKET: spider_name, keys.OUT_OF_STOCK: {"$ne": True}}
        )
        item_count = stats.get("item_scraped_count", 0)
        is_visible_name = spider_name in keys.VISIBLE_MARKETS
        is_less_item = item_count < (existing_item_count / 5)
        is_problem = is_visible_name and is_less_item
        if is_problem:
            subject = f"{spider_name} seen {item_count} out of {existing_item_count}"
            send_email(subject, str(stats))
