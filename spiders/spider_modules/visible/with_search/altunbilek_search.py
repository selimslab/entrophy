import json

import scrapy

import constants as keys
from spiders.spider_modules.base import BaseSpider
from spiders.spider_modules.search_helper import (
    CUSTOM_SEARCHBOX_SETTINGS,
    BarcodeSearchHelper,
)
from spiders.test_spider import debug_spider


class TopLocalSearcher(BaseSpider):
    name = "search_altun"
    custom_settings = CUSTOM_SEARCHBOX_SETTINGS

    def __init__(self, *args, **kwargs):
        super(TopLocalSearcher, self).__init__(*args, base_domain="altunbilekler.com")
        barcodes_to_search = BarcodeSearchHelper.get_barcodes_to_search(
            keys.ALTUNBILEK, keys.TRADITIONAL_MARKETS
        )
        self.barcode_generator = BarcodeSearchHelper.barcode_generator(
            barcodes_to_search
        )

    def start_requests(self):
        base = "https://www.altunbilekler.com/api/content/GetTopProductSearch?SearchKeyword="
        # 8692971433264

        for barcode in self.barcode_generator:
            url = base + barcode
            yield scrapy.Request(
                url, callback=self.parse, meta={keys.BARCODES: barcode}
            )

    def parse(self, response):
        json_response = json.loads(response.body_as_unicode())
        searchContent = json_response.get("searchContent")
        resp = scrapy.Selector(text=searchContent)

        name = resp.css(".complate_text::text").extract_first()

        link = None
        href = resp.css(".ui-menu-item::attr(data-url)").extract_first()
        if href:
            link = self.base_url + href

        src = resp.css(".complate_image img::attr(src)").extract_first()
        if src:
            src = self.base_url + src

        price = resp.css(".complate_productPrice::text").extract_first()

        if price:
            price = price.replace(",", ".").replace("₺", "").strip()
        if link and price:
            yield {
                keys.LINK: link,
                keys.NAME: name,
                keys.PRICE: price,
                keys.SRC: src,
                keys.MARKET: keys.ALTUNBILEK,
                keys.BARCODES: response.meta.get(keys.BARCODES),
            }


if __name__ == "__main__":
    debug_spider(TopLocalSearcher)
