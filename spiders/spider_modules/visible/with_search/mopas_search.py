import scrapy

import constants as keys
from spiders.spider_modules.base import BaseSpider
from spiders.spider_modules.search_helper import (
    BarcodeSearchHelper,
    CUSTOM_SEARCHBOX_SETTINGS,
)
from spiders.spider_modules.visible.with_search.mopas_helper import MopasHelper


class MopasSearcher(BaseSpider):
    name = "search_mopas"
    custom_settings = CUSTOM_SEARCHBOX_SETTINGS

    def __init__(self, *args, **kwargs):
        barcodes_to_search = BarcodeSearchHelper.get_barcodes_to_search(
            keys.MOPAS, keys.TRADITIONAL_MARKETS
        )
        self.barcode_generator = BarcodeSearchHelper.barcode_generator(
            barcodes_to_search
        )
        super(MopasSearcher, self).__init__(*args, base_domain="mopas.com.tr")

    def start_requests(self):
        base = "https://mopas.com.tr/search/?text="

        for barcode in self.barcode_generator:
            url = base + barcode
            yield scrapy.Request(
                url, callback=self.parse, meta={keys.BARCODES: [barcode]}
            )

    def parse(self, response):
        grid = response.css(".product-list-grid")
        products = grid.css(".card")

        for product_div in products:
            product = MopasHelper.extract_product_info(product_div, self.base_url)
            if product:
                product[keys.BARCODES] = response.meta.get(keys.BARCODES)
                yield product
