import scrapy

import constants as keys
from spiders.spider_modules.base import BaseSpider
from spiders.spider_modules.search_helper import (
    CUSTOM_SEARCHBOX_SETTINGS,
    BarcodeSearchHelper,
)
from spiders.spider_modules.visible.with_search.eve_searcher import EveShopSearcher
from spiders.test_spider import debug_spider


class CosmeticaSearcher(BaseSpider):
    name = "search_cosmetica"
    custom_settings = CUSTOM_SEARCHBOX_SETTINGS

    def __init__(self, *args, **kwargs):
        super(CosmeticaSearcher, self).__init__(*args, base_domain="cosmetica.com.tr")
        barcodes_to_search = BarcodeSearchHelper.get_barcodes_to_search(
            keys.COSMETICA, keys.COSMETICS_MARKETS
        )
        self.barcode_generator = BarcodeSearchHelper.barcode_generator(
            barcodes_to_search
        )

    def start_requests(self):
        base = "https://www.cosmetica.com.tr/userControls/kutu/ascArama_ajx.aspx?searchType=0&suggType=2&srt=ES&lang=tr-TR&text="

        for barcode in self.barcode_generator:  # {"3600531509170"}:
            url = base + barcode
            yield scrapy.Request(
                url, callback=self.parse, meta={keys.BARCODES: barcode}
            )

    def parse(self, response):
        product = EveShopSearcher.get_product(response, self.base_url, keys.COSMETICA)
        if product:
            yield product


if __name__ == "__main__":
    debug_spider(CosmeticaSearcher)
