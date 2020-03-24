import scrapy

import constants as keys
from spiders.spider_modules.base import BaseSpider
from spiders.spider_modules.search_helper import (
    CUSTOM_SEARCHBOX_SETTINGS,
    BarcodeSearchHelper,
)
from spiders.spider_modules.visible.with_search.joker import TopLocalHelper
from spiders.test_spider import debug_spider


class JokerSearcher(BaseSpider):
    name = "search_joker"
    custom_settings = CUSTOM_SEARCHBOX_SETTINGS

    def __init__(self, *args, **kwargs):
        super(JokerSearcher, self).__init__(*args, base_domain="joker.com.tr")
        barcodes_to_search = BarcodeSearchHelper.get_barcodes_to_search(
            keys.JOKER, keys.BABY_MARKETS
        )
        self.barcode_generator = BarcodeSearchHelper.barcode_generator(
            barcodes_to_search
        )

    def start_requests(self):
        base = "https://www.joker.com.tr/arama/?keyword="

        for barcode in self.barcode_generator:
            url = base + barcode
            yield scrapy.Request(
                url, callback=self.parse, meta={keys.BARCODES: barcode}
            )

    def parse(self, response):
        grid = response.css(".j-product-list")
        products = grid.css(".item.product")

        for product_div in products:
            product = TopLocalHelper.extract_product_info(product_div, self.base_url)
            if product:
                product[keys.BARCODES] = response.meta.get(keys.BARCODES)
                yield product


if __name__ == "__main__":
    debug_spider(JokerSearcher)
