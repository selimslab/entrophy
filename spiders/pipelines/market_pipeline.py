from datetime import datetime

import constants as keys
from services.barcode_cleaner import BarcodeCleaner
from .base_pipeline import BasePipeline
from .size_adder import SizeAdder
import data_services
from data_services.firebase.connect import skus_collection


class ItemCountException(Exception):
    pass


class ItemContentException(Exception):
    pass


class MarketPipeline(BasePipeline):
    def __init__(
        self, batch_size=128, size_adder=SizeAdder(),
    ):
        super().__init__(batch_size)
        self.size_adder = size_adder
        self.instant_update_active = True
        self.batch = []
        self.batch_size = batch_size
        self.important_keys = {keys.LINK, keys.NAME, keys.PRICE, keys.MARKET, keys.SRC}
        self.bad_item_count = 0

    def log_historical_price(self, item):
        price = item.get(keys.PRICE)
        if price:
            # replace dots because it will be used in mongo dot notation
            price = str(price).replace(".", ",")
            log_key = keys.HISTORICAL_PRICES + "." + price
            item[log_key] = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")

        return item

    def get_updates_for_existing_item(self, item):
        selector = {keys.LINK: item.pop(keys.LINK)}
        command = dict()

        barcodes = item.get(keys.BARCODES, [])
        if barcodes:
            command["$addToSet"] = {keys.BARCODES: {"$each": barcodes}}
            item.pop(keys.BARCODES)

        item = self.clean_promoted(item)
        item = self.log_historical_price(item)

        command["$set"] = item

        return selector, command

    @staticmethod
    def instant_price_update(existing_link_id_pairs, instant_update_batch):

        existing_ids = list(existing_link_id_pairs.values())

        existing_elastic_docs = data_services.search_elastic_by_ids(existing_ids)

        id_price_pairs = {
            doc.get("_id"): doc.get("_source", {}).get("prices", {})
            for doc in existing_elastic_docs
        }

        instant_updates = []

        for link, item in instant_update_batch:
            sku_id = existing_link_id_pairs.get(link)
            old_prices = id_price_pairs.get(sku_id)
            if old_prices:
                price_update = {item.get(keys.MARKET): item.get(keys.PRICE)}
                new_prices = {**old_prices, **price_update}
                update = {keys.SKU_ID: sku_id, keys.PRICES: new_prices}
                instant_updates.append(update)

        data_services.elastic.update_docs(instant_updates, index="products")
        data_services.batch_update_firestore(
            instant_updates, collection=skus_collection
        )

    def process_batch(self):
        links = [item.get(keys.LINK) for item in self.batch]
        existing_links_cursor = data_services.get_sku_ids_by_links(links)

        existing_link_id_pairs = {
            doc.get(keys.LINK): doc.get(keys.SKU_ID) for doc in existing_links_cursor
        }

        instant_update_batch = []

        for item in self.batch:
            link = item.get(keys.LINK)
            if link in existing_link_id_pairs:
                instant_update_batch.append((link, item))
                selector, command = self.get_updates_for_existing_item(item)
                self.mongo_sync.add_update(selector, command)
            else:
                # new doc
                selector = {keys.LINK: item.get(keys.LINK)}
                command = {"$set": item}
                self.mongo_sync.add_update(selector, command)

        self.instant_price_update(existing_link_id_pairs, instant_update_batch)

    def process_item(self, item, spider):
        item = self.clean_item(item)
        if not item:
            return
        item = self.size_adder.add_size(item)

        item[keys.BARCODES] = BarcodeCleaner.get_clean_barcodes(
            item.get(keys.BARCODES, [])
        )

        # remove empty and None values
        item = self.clean_item(item)
        if any(key not in item for key in self.important_keys):
            self.bad_item_count += 1
            return item

        self.batch.append(item)
        if len(self.batch) > self.batch_size:
            self.process_batch()
            self.batch = []

        return item

    def close_spider(self, spider):
        if self.bad_item_count > 100:
            raise ItemContentException(f"{self.bad_item_count} bad items")

        stats = spider.crawler.stats.get_stats()
        self.check_count(spider.name, stats)

        self.process_batch()
        self.mongo_sync.bulk_exec()

    @staticmethod
    def check_count(spider_name, stats):
        count_items_in_stock = data_services.get_in_stock(market=spider_name)
        item_count = stats.get("item_scraped_count", 0)
        is_visible_name = spider_name in keys.VISIBLE_MARKETS
        is_less_item = item_count < (count_items_in_stock / 5)
        is_problem = is_visible_name and is_less_item
        if is_problem:
            raise ItemCountException(
                f"""
                {spider_name} seen {item_count} out of {count_items_in_stock}
                stats: {str(stats)}        
            """
            )


if __name__ == "__main__":
    pass
