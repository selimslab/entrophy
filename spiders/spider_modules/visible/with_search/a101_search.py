import scrapy

import constants as keys
from spiders.spider_modules.base import BaseSpider
from spiders.spider_modules.search_helper import (
    CUSTOM_SEARCHBOX_SETTINGS,
    BarcodeSearchHelper,
)
from spiders.spider_modules.visible.with_search.a101_helper import A101Helper


class A101Searcher(BaseSpider):
    name = "search_a101"
    custom_settings = CUSTOM_SEARCHBOX_SETTINGS

    def __init__(self, *args, **kwargs):
        barcodes_to_search = BarcodeSearchHelper.get_barcodes_to_search(
            keys.A101, keys.TRADITIONAL_MARKETS
        )
        self.barcode_generator = BarcodeSearchHelper.barcode_generator(
            barcodes_to_search
        )
        super(A101Searcher, self).__init__(*args, base_domain="a101.com.tr")

    def start_requests(self):
        base = "https://www.a101.com.tr/list/?search_text="
        for barcode in self.barcode_generator:
            url = base + barcode
            yield scrapy.Request(
                url, callback=self.parse, meta={keys.BARCODES: barcode}
            )

    def parse(self, response):
        table = response.css(".product-list-general")
        products = table.css(".set-product-item")

        if len(products) > 1:
            return

        for product in products:
            p = A101Helper.extract_product_info(product, self.base_url)
            p[keys.BARCODES] = response.meta.get(keys.BARCODES)
            yield p
