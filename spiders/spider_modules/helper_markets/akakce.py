import urllib.parse

import scrapy

import constants as keys
import data_services.mongo.collections as collections
from spiders.spider_modules.base import BaseSpider
from spiders.spider_modules.search_helper import BarcodeSearchHelper
from spiders.test_spider import debug_spider

AKAKCE_SETTINGS = {
    "ITEM_PIPELINES": {"src.spiders.pipelines.search_pipeline.SearchPipeline": 300},
    "DOWNLOAD_DELAY": 2,
    "CRAWLERA_ENABLED": False,
    "CRAWLERA_PRESERVE_DELAY": True,
    "DOWNLOADER_MIDDLEWARES": {"scrapy_crawlera.CrawleraMiddleware": 300},
    "CRAWLERA_APIKEY": "c09eca1df4e344149c7059a763e9f632",  # TR IP
}


class AkakceSearcher(BaseSpider):
    name = "search_akakce"
    custom_settings = AKAKCE_SETTINGS

    def __init__(self, *args, **kwargs):
        super(AkakceSearcher, self).__init__(*args, base_domain="akakce.com")
        self.debug = kwargs.get("debug")
        if self.debug:
            self.barcode_generator = {"3600523193370", "8699543630090", "8001841324180"}
        else:
            barcodes_to_search = collections.items_collection.distinct(keys.BARCODES)
            self.barcode_generator = BarcodeSearchHelper.barcode_generator(
                barcodes_to_search
            )

    def start_requests(self):
        base = "https://www.akakce.com/arama/?q="
        for barcode in self.barcode_generator:
            url = base + barcode
            yield scrapy.Request(
                url, callback=self.parse, meta={keys.BARCODES: barcode}
            )

    def parse(self, response):
        ul = response.css("#APL")
        lis = ul.css("li[data-pr]")
        if lis and len(lis) == 1:
            li = lis.pop()
            href = li.css("a::attr(href)").extract_first()
            p = dict()
            link = "https://www.akakce.com" + href
            p[keys.LINK] = link
            p[keys.MARKET] = keys.AKAKCE
            p[keys.BARCODES] = [response.meta.get(keys.BARCODES)]
            yield scrapy.Request(link, callback=self.visit_detail, meta={"product": p})

    def visit_detail(self, response):
        ul = response.css("#MP_h")
        lis = ul.css("li")
        base = "https://www.akakce.com/c/?"

        promoted = dict()
        for li in lis:
            title = li.css("img::attr(title)").extract_first().lower().strip()
            if not any(s in title for s in keys.ALLOWED_MARKET_LINKS):
                continue

            href = li.css("a::attr(href)").extract_first()
            if href:
                href = href.split("?")[1]
                url = base + href
                unquoted = urllib.parse.unquote(urllib.parse.unquote(url))
                url = "https" + unquoted.split("r=https")[1]
                promoted[title] = url

        if promoted:
            p = response.meta.get("product")
            p[keys.PROMOTED] = promoted
            yield p


if __name__ == "__main__":
    debug_spider(AkakceSearcher)
