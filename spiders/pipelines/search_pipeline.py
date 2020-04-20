import constants as keys
from services import name_cleaner
from services.barcode_cleaner import BarcodeCleaner
from supermatch.sizing import SizeFinder, SizingException
from spiders.pipelines.base_pipeline import BasePipeline


class SearchPipeline(BasePipeline):
    def __init__(self, write_interval=10):
        super().__init__(write_interval)
        self.size_finder = SizeFinder()

    def get_updates_for_existing_item(self, item):
        selector = {keys.LINK: item.pop(keys.LINK)}
        command = dict()

        if keys.GOOGLE_INFO in item:
            google_info = item.pop(keys.GOOGLE_INFO)
            barcodes = BarcodeCleaner.get_google_barcodes_from_info(google_info)
            if barcodes:
                item[keys.BARCODES] = barcodes
        else:
            barcodes = item.get(keys.BARCODES, [])
            if barcodes:
                command["$addToSet"] = {keys.BARCODES: {"$each": barcodes}}
                item.pop(keys.BARCODES)

        item = self.clean_promoted(item)

        command["$set"] = item

        return selector, command

    def add_size(self, item):
        name = item.get(keys.NAME, "")
        market = item.get(keys.MARKET)
        if name and market not in keys.HELPER_MARKETS:
            size_name = name_cleaner.size_cleaner(name)
            try:
                result = self.size_finder.get_digits_and_unit(size_name)
                if result:
                    digits, unit = result
                    item[keys.DIGITS], item[keys.UNIT], item[keys.SIZE] = (
                        digits,
                        unit,
                        " ".join([str(digits), unit]),
                    )
            except SizingException:
                pass

        return item

    def sync_item(self, item: dict):
        selector, command = self.get_updates_for_existing_item(item.copy())
        self.mongo_sync.add_update_one(selector, command)
        return item

    def process_item(self, item, spider):
        item = self.clean_item(item)
        if not item:
            return
        item = self.add_size(item)

        item[keys.BARCODES] = BarcodeCleaner.get_clean_barcodes(
            item.get(keys.BARCODES, [])
        )

        # remove empty and None values
        item = self.clean_item(item)

        return self.sync_item(item)

    def close_spider(self, spider):
        stats = spider.crawler.stats.get_stats()
        print("STATS", stats)
        self.mongo_sync.bulk_exec()


if __name__ == "__main__":
    pass
