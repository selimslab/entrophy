import json

import requests

import constants as keys
from data_services import mark_out_of_stock
from spiders.spider_modules.base import BaseSpider
from spiders.test_spider import debug_spider


class SokHelper:
    @staticmethod
    def get_urls_sok():

        urls = [
            # kağıthane
            "https://www.ceptesok.com/api/v1/products?store_id=12065",
            # batıkent
            # "https://www.ceptesok.com/api/v1/products?store_id=11924",
        ]

        r = requests.get(urls[0])
        body = json.loads(r.content)
        page_count = body.get("pagination", {}).get("pageCount", 30)
        cat_urls = [
            url + "&page=%s" % page for page in range(1, page_count + 1) for url in urls
        ]
        return cat_urls


class CepteSokSpider(BaseSpider):
    name = keys.CEPTESOK

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, base_domain="ceptesok.com")
        self.start_urls = SokHelper.get_urls_sok()

    def close(self, reason):
        self.logger.info("Spider closed: %s due to %s", self.name, reason)
        if reason == "finished":
            mark_out_of_stock(self.links_seen, market_name="şok")

    @staticmethod
    def extract_product_info(product_json, base_url):

        brand = product_json.get("brand_name")
        name = product_json.get("name")
        if brand and brand not in name:
            name = brand + " " + name

        price = product_json.get("selected_serial").get("price")
        link = base_url + "/" + product_json.get("link_name")

        product = {
            keys.LINK: link,
            keys.NAME: name,
            keys.PRICE: price,
            keys.MARKET: keys.CEPTESOK,
            keys.OUT_OF_STOCK: False,
        }

        files = product_json.get("files")
        if files:
            href = files.pop(0).get("document_href")
            src = "https://cdnd.ceptesok.com/product/420x420/" + href
            product[keys.SRC] = src

        if product_json.get("stock") == 0:
            product[keys.OUT_OF_STOCK] = True

        return product

    def parse(self, response):
        data = json.loads(response.text)
        products = data.get("payload").get("products")

        for product_json in products:
            product = self.extract_product_info(product_json, self.base_url)
            self.links_seen.add(product.get(keys.LINK))
            yield product


if __name__ == "__main__":
    debug_spider(CepteSokSpider)
