from datetime import datetime

import constants as keys
from instant_update.instant_update import instant_updater
from services.barcode_cleaner import BarcodeCleaner
from .base_pipeline import BasePipeline
from .item_count_monitor import ItemCountMonitor
from .size_adder import SizeAdder


class MarketPipeline(BasePipeline):
    def __init__(
        self,
        write_interval=64,
        size_adder=SizeAdder(),
        instant_updater=instant_updater,
        item_count_monitor=ItemCountMonitor(),
    ):
        super().__init__(write_interval)
        self.size_adder = size_adder
        self.instant_update_active = True
        self.instant_updater = instant_updater
        self.item_count_monitor = item_count_monitor

    def open_spider(self, spider):
        # if debug, instant update will be False, because snapshots are expensive
        if spider.instant_update_active is not None:
            self.instant_update_active = spider.instant_update_active

        if self.instant_update_active:
            self.instant_updater.get_snapshot()

    def get_updates_for_existing_item(self, item):
        selector = {keys.LINK: item.pop(keys.LINK)}
        command = dict()

        barcodes = item.get(keys.BARCODES, [])
        if barcodes:
            command["$addToSet"] = {keys.BARCODES: {"$each": barcodes}}
            item.pop(keys.BARCODES)

        item = self.clean_promoted(item)

        price = item.get(keys.PRICE)
        if price:
            # replace dots because it will be used in mongo dot notation
            price = str(price).replace(".", ",")
            log_key = keys.HISTORICAL_PRICES + "." + price
            item[log_key] = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")

        command["$set"] = item

        return selector, command

    def sync_item(self, item: dict):
        link = item.get(keys.LINK)

        existing_doc = self.instant_updater.link_doc_pairs.get(link)

        if existing_doc:
            selector, command = self.get_updates_for_existing_item(item.copy())
            self.mongo_sync.add_update(selector, command)
            if self.instant_update_active:
                price_update = {item.get(keys.MARKET): item.get(keys.PRICE)}
                self.instant_updater.produce_event(price_update, existing_doc)
        else:
            # new doc
            selector = {keys.LINK: item.get(keys.LINK)}
            command = {"$set": item}
            self.mongo_sync.add_update(selector, command)

        return item

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

        return self.sync_item(item)

    def close_spider(self, spider):
        stats = spider.crawler.stats.get_stats()
        self.item_count_monitor.check_for_anomalies(spider.name, stats)

        self.mongo_sync.bulk_exec()
        self.instant_updater.instant_update_elastic()
        self.instant_updater.instant_update_firestore()


if __name__ == "__main__":
    pass
