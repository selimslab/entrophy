import scrapy

import constants as keys
from spiders.spider_modules.base import BaseSpider
from spiders.spider_modules.search_helper import (
    CUSTOM_SEARCHBOX_SETTINGS,
    BarcodeSearchHelper,
)
from spiders.spider_modules.visible.with_search.c4_helper import CarrefourHelper
from spiders.test_spider import debug_spider


class CarrefourSearcher(BaseSpider):
    name = "search_c4"
    custom_settings = CUSTOM_SEARCHBOX_SETTINGS

    def __init__(self, *args, **kwargs):
        barcodes_to_search = BarcodeSearchHelper.get_barcodes_to_search(
            keys.CARREFOUR, keys.TRADITIONAL_MARKETS
        )
        self.barcode_generator = BarcodeSearchHelper.barcode_generator(
            barcodes_to_search
        )
        super(CarrefourSearcher, self).__init__(*args, base_domain="carrefoursa.com")

    def start_requests(self):
        base = "https://www.carrefoursa.com/tr/search/?text="

        for barcode in self.barcode_generator:
            url = base + barcode
            yield scrapy.Request(
                url, callback=self.parse, meta={keys.BARCODES: barcode}
            )

    def parse(self, response):
        table = response.css("ul.product-listing")
        products = table.css("div.product-card")
        if len(products) > 1:
            return

        for product_div in products:
            product = CarrefourHelper.extract_product_info(product_div, self.base_url)
            if product:
                product[keys.BARCODES] = response.meta.get(keys.BARCODES)
                yield product


if __name__ == "__main__":
    debug_spider(CarrefourSearcher)
