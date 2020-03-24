import re

import scrapy

import constants as keys
from spiders.spider_modules.base import BaseSpider
from spiders.test_spider import debug_spider


class SevilHelper:
    @staticmethod
    def extract_product_info(product_div):
        link = product_div.css("h2.product-name a::attr(href)").extract_first()
        name = product_div.css("h2.product-name a::text").extract_first()

        price_div = product_div.css(".regular-price")
        if not price_div:
            price_div = product_div.css(".special-price")

        price = price_div.css(".price::text").extract_first()
        if price:
            price = price.replace("TL", "")
            if "," in price and "." in price:
                price = price.split(",")[0].replace(".", "")
            else:
                price = price.replace(",", ".")

            price = price.strip()
            try:
                price = int(price)
            except ValueError:
                price = float(price)

        src = product_div.css(".product-image-wrapper a>img::attr(src)").extract_first()

        p = {
            keys.LINK: link,
            keys.NAME: name,
            keys.SRC: src,
            keys.PRICE: price,
            keys.MARKET: keys.SEVIL,
        }

        barcode = re.findall("[0-9]{13}", src)
        if not barcode:
            barcode = re.findall("[0-9]{14}", src)
        if barcode:
            p[keys.BARCODES] = barcode

        return p


class TopLocalSpider(BaseSpider):
    name = keys.SEVIL

    custom_settings = {
        "DOWNLOAD_DELAY": 1,
        "CRAWLERA_ENABLED": True,
        "CRAWLERA_PRESERVE_DELAY": True,
        "DOWNLOADER_MIDDLEWARES": {"scrapy_crawlera.CrawleraMiddleware": 300},
        "CRAWLERA_APIKEY": "c09eca1df4e344149c7059a763e9f632",  # TR IPs
    }

    def __init__(self, *args, **kwargs):
        super(TopLocalSpider, self).__init__(*args, base_domain="sevil.com.tr")

    def start_requests(self):
        cats = {"/parfumler", "/makyaj", "/cilt-vucut-sac-bakimi"}
        for cat in cats:
            cat_url = self.base_url + cat
            yield scrapy.Request(cat_url, callback=self.parse)

    def parse(self, response):
        grid = response.css(".products-grid")
        products = grid.css(".item")
        for product_div in products:
            product = SevilHelper.extract_product_info(product_div)
            yield product

        next_page_url = response.css("a.next::attr(href)").extract_first()
        if next_page_url:
            yield response.follow(next_page_url, callback=self.parse)


if __name__ == "__main__":
    debug_spider(TopLocalSpider)
