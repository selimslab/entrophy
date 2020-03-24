import re

import bs4
import requests
import scrapy

import constants as keys
import data_services.mongo.collections as collections
from spiders.spider_modules.base import BaseSpider
from spiders.test_spider import debug_spider


def get_urls_marketpaketi():
    url = "https://www.marketpaketi.com.tr"
    r = requests.get(url)
    soup = bs4.BeautifulSoup(r.content, features="lxml")
    links = soup.findAll("a", {"class": "dMenu"})
    bad_cats = {"ev", "kirtasiye", "oyuncak", "elektronik", "mutfak", "tekstil"}
    for link in links:
        url = link.get("href")
        if not any(cat in url for cat in bad_cats):
            yield url


class MarketPaketiSpider(BaseSpider):
    name = keys.MARKET_PAKETI
    start_urls = get_urls_marketpaketi()

    def __init__(self, *args, **kwargs):
        super(MarketPaketiSpider, self).__init__(
            *args, base_domain="marketpaketi.com.tr"
        )

    def parse(self, response):
        grid = response.css(".urun_liste")
        products = grid.css(".liste_urun")

        for product in products:
            product_info = extract_product_info(product)
            if product_info:
                yield product_info

        if self.next_page:
            next_page_url = response.css("a[rel='next']::attr(href)").extract_first()
            if next_page_url:
                yield response.follow(next_page_url, callback=self.parse)


def extract_product_info(product):
    p = dict()
    p[keys.MARKET] = keys.MARKET_PAKETI
    p[keys.LINK] = product.css("a.urun_gorsel::attr(href)").extract_first()
    p[keys.NAME] = product.css("a.urun_adi_ic::text").extract_first()
    return p


def get_mp_detail_url():
    query = {keys.MARKET: keys.MARKET_PAKETI, keys.BARCODES: {"$exists": False}}
    projection = {keys.LINK: 1}
    cursor = collections.items_collection.find(query, projection)
    for doc in cursor:
        yield doc.get(keys.LINK)


class BarkodPaketiSpider(BaseSpider):
    name = "mpd"
    custom_settings = {
        "DOWNLOAD_TIMEOUT": 20,
        "DOWNLOAD_DELAY": 1,
        "ITEM_PIPELINES": {"src.pipelines.market_pipeline.MarketPipeline": 300},
    }

    def __init__(self, *args, **kwargs):
        super(BarkodPaketiSpider, self).__init__(
            *args, base_domain="marketpaketi.com.tr"
        )

    def start_requests(self):
        for detail_url in get_mp_detail_url():
            yield scrapy.Request(
                detail_url, callback=self.parse, meta={keys.LINK: detail_url}
            )

    def parse(self, response):
        code = response.css(".stok_kod::text").extract_first()
        if code:
            code = code.split(":")[1].strip()
            digit_barcodes = re.findall(r"\d+", code)
            if digit_barcodes:
                barcode = sorted(digit_barcodes, key=len).pop()
                result = dict()
                result[keys.LINK] = response.meta.get(keys.LINK)
                result[keys.BARCODES] = barcode
                yield result


if __name__ == "__main__":
    debug_spider(MarketPaketiSpider)
