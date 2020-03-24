from urllib.parse import quote_plus

import scrapy

import constants as keys
import data_services.mongo.collections as collections
from spiders.spider_modules.google.google_base_searcher import GoogleSearcher
from spiders.spider_modules.google.google_settings import GOOGLE_SETTINGS
from spiders.spider_modules.search_helper import BarcodeSearchHelper
from spiders.test_spider import debug_spider


class GoogleBarcodeSearcher(GoogleSearcher):
    """
    Search barcodes in google and save links to the detail pages
    """

    name = "google_barcode_search"

    custom_settings = GOOGLE_SETTINGS

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.debug = kwargs.get("debug")
        if self.debug:
            self.barcode_generator = {"3600523193370"}
        else:
            barcodes_to_search = collections.items_collection.distinct(keys.BARCODES)
            print("barcodes_to_search", len(barcodes_to_search))
            self.barcode_generator = BarcodeSearchHelper.barcode_generator(
                barcodes_to_search
            )

    def start_requests(self):
        base_search_url = self.base_url + "/search?tbm=shop&hl=en-TR&q="
        for barcode in self.barcode_generator:
            search_url = base_search_url + quote_plus(barcode)
            yield scrapy.Request(search_url, callback=self.parse)


if __name__ == "__main__":
    debug_spider(GoogleBarcodeSearcher)
