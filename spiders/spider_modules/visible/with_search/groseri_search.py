import scrapy

import constants as keys
from spiders.spider_modules.base import BaseSpider
from spiders.spider_modules.search_helper import (
    CUSTOM_SEARCHBOX_SETTINGS,
    BarcodeSearchHelper,
)
from spiders.spider_modules.visible.with_search.groseri_helper import TopLocalHelper
from spiders.test_spider import debug_spider


class TopLocalSearcher(BaseSpider):
    name = "search_groseri"
    custom_settings = CUSTOM_SEARCHBOX_SETTINGS

    def __init__(self, *args, **kwargs):
        barcodes_to_search = BarcodeSearchHelper.get_barcodes_to_search(
            keys.GROSERI, keys.TRADITIONAL_MARKETS
        )
        self.barcode_generator = BarcodeSearchHelper.barcode_generator(
            barcodes_to_search
        )
        super(TopLocalSearcher, self).__init__(*args, base_domain="groseri.com")

    def start_requests(self):
        base = "https://www.groseri.com.tr/urunler/ara?q="
        for barcode in self.barcode_generator:
            url = base + barcode
            yield scrapy.Request(
                url, callback=self.parse, meta={keys.BARCODES: barcode}
            )

    def parse(self, response):
        products = response.css(".urunler")
        if not products:
            return

        if len(products) > 1:
            return

        for product in products:
            p = TopLocalHelper.extract_product_info(product, self.base_url)
            p[keys.BARCODES] = response.meta.get(keys.BARCODES)
            yield p


if __name__ == "__main__":
    debug_spider(TopLocalSearcher)
