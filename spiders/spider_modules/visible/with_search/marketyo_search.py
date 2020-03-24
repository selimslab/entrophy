import json
import random

import scrapy

import constants as keys
from spiders.spider_modules.base import BaseSpider
from spiders.spider_modules.search_helper import (
    CUSTOM_SEARCHBOX_SETTINGS,
    BarcodeSearchHelper,
)
from spiders.test_spider import debug_spider


class MarketyoSearcher(BaseSpider):
    name = "search_marketyo"
    custom_settings = CUSTOM_SEARCHBOX_SETTINGS

    def __init__(self, *args, **kwargs):
        super(MarketyoSearcher, self).__init__(base_domain="marketyo.net")
        self.markets_to_search = keys.MARKETYO_MARKET_HEADERS
        self.debug = kwargs.get("debug")
        self.queues = self.get_search_queues()

    def get_search_queues(self):
        queues = dict()
        for header in self.markets_to_search:
            market_name = header.get("client")
            if self.debug:
                barcodes_to_search = {"8690767675089", "8690624101874"}
            else:
                barcodes_to_search = BarcodeSearchHelper.get_barcodes_to_search(
                    market_name, keys.TRADITIONAL_MARKETS
                )
            queues[market_name] = BarcodeSearchHelper.barcode_generator(
                barcodes_to_search
            )

        return queues

    def start_requests(self):
        random.shuffle(self.markets_to_search)
        search_url = "https://core.marketyo.net/api/v1/Products/Search"

        for header in self.markets_to_search:
            market_name = header.get("client")
            for barcode in self.queues.get(market_name):
                header["Content-Type"] = "application/json"
                payload = {"query": barcode}  # 8690767675089 8690624101874
                meta = header.copy()
                meta[keys.BARCODES] = [barcode]
                yield scrapy.Request(
                    search_url,
                    method="POST",
                    callback=self.parse,
                    headers=header,
                    meta=meta,
                    body=json.dumps(payload),
                    dont_filter=True,
                )

    def parse(self, response):
        json_response = json.loads(response.body_as_unicode())
        data = json_response.get("data")

        if not data:
            return

        market = response.meta.get("client")
        products = data.get("products")

        if len(products) != 1:
            return

        product_json = products.pop()

        yield {
            keys.LINK: product_json.get("id"),
            keys.NAME: product_json.get("name"),
            keys.PRICE: product_json.get("price"),
            keys.MARKET: market,
            keys.BARCODES: response.meta.get(keys.BARCODES),
        }


if __name__ == "__main__":
    debug_spider(MarketyoSearcher)
