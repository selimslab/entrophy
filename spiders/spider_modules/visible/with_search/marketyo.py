# coding: utf8
import json
from random import shuffle

import requests
import scrapy

import constants as keys
from spiders.spider_modules.base import BaseSpider
from spiders.test_spider import debug_spider


class MarketyoSpider(BaseSpider):
    name = "marketyo"
    custom_settings = {"DOWNLOAD_DELAY": 2}

    def __init__(self, *args, **kwargs):
        super(MarketyoSpider, self).__init__(base_domain="marketyo.net")

    def start_requests(self):
        shuffle(keys.MARKETYO_MARKET_HEADERS)
        for headers in keys.MARKETYO_MARKET_HEADERS:
            print(headers)
            for categoryId in self.category_id_generator(headers):
                products_url = "https://core.marketyo.net/api/v1/Products?categoryId="
                cat_url = products_url + categoryId
                yield scrapy.Request(
                    cat_url, callback=self.parse, headers=headers, meta=headers
                )

    def parse(self, response):
        json_response = json.loads(response.body_as_unicode())
        products = json_response.get("data")
        market = response.meta.get("client")
        if not products:
            products = []
        for product in self.parse_products(products, market):
            yield product

    @staticmethod
    def parse_products(products, market):
        for product in products:
            p = dict()
            p[keys.LINK] = product.get("id")
            p[keys.NAME] = product.get("name")
            p[keys.PRICE] = product.get("price")
            p[keys.BRAND] = product.get("brand", {}).get("name")
            images = product.get("images")
            if images:
                p[keys.SRC] = images.pop()
            p[keys.MARKET] = market
            yield p

    @staticmethod
    def category_id_generator(headers):
        category_url = "https://core.marketyo.net/api/v1/Categories"
        r = requests.get(category_url, headers=headers)
        data = json.loads(r.content)
        cats = data.get("data")
        parents = set()
        ids = dict()
        for cat in cats:
            parent = cat.get("idParent")
            parents.add(parent)
            id = cat.get("id")
            name = cat.get("name")
            ids[id] = name

        categoryIds = set(ids.keys()) - parents
        for id in categoryIds:
            yield id


def test_cats():
    for headers in keys.MARKETYO_MARKET_HEADERS:
        print(headers.get("client"))
        MarketyoSpider.category_id_generator(headers)
        print("\n")


if __name__ == "__main__":
    debug_spider(MarketyoSpider)
