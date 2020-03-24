import scrapy

import constants as keys
from spiders.spider_modules.base import BaseSpider
from spiders.spider_modules.search_helper import (
    BarcodeSearchHelper,
    CUSTOM_SEARCHBOX_SETTINGS,
)
from spiders.spider_modules.visible.with_search.watsons_helper import WatsonsHelper


class WatsonsSearcher(BaseSpider):
    name = "search_watsons"
    custom_settings = CUSTOM_SEARCHBOX_SETTINGS

    def __init__(self, *args, **kwargs):
        barcodes_to_search = BarcodeSearchHelper.get_barcodes_to_search(
            keys.WATSONS, keys.COSMETICS_MARKETS
        )
        self.barcode_generator = BarcodeSearchHelper.barcode_generator(
            barcodes_to_search
        )
        super(WatsonsSearcher, self).__init__(*args, base_domain="watsons.com.tr")

    def start_requests(self):
        base = "https://www.watsons.com.tr/search?q="

        for barcode in self.barcode_generator:
            url = base + barcode
            yield scrapy.Request(
                url, callback=self.parse, meta={keys.BARCODES: [barcode]}
            )

    def parse(self, response):
        grid = response.css(".product-list-container")
        search_results = grid.css(".product-box-container")

        if search_results and len(search_results) == 1:
            product_div = search_results.pop()
            product = WatsonsHelper.extract_product_info(product_div, self.base_url)
            product[keys.BARCODES] = response.meta.get(keys.BARCODES)
            yield product
