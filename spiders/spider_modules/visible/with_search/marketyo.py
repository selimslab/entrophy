# coding: utf8
import json
from random import shuffle

import requests
import scrapy

import constants as keys
from spiders.spider_modules.base import BaseSpider
from spiders.test_spider import debug_spider

from pprint import pprint


class MarketyoSpider(BaseSpider):
    name = "marketyo"

    def __init__(self, *args, **kwargs):
        super(MarketyoSpider, self).__init__(base_domain="marketyo.net")

    def start_requests(self):
        shuffle(keys.MARKETYO_MARKET_HEADERS)
        for headers in keys.MARKETYO_MARKET_HEADERS:
            print(headers)
            for category_id in self.category_id_generator(headers):
                products_url = "https://core.marketyo.net/api/v1/Products?categoryId="
                cat_url = products_url + category_id
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
            cats = [cat.get("name") for cat in product.get("categories", [])]
            cats = [c for c in cats if c]
            p[keys.CATEGORIES] = cats
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
            cat_id = cat.get("id")
            name = cat.get("name")
            ids[cat_id] = name

        category_ids = set(ids.keys()) - parents
        for cat_id in category_ids:
            yield cat_id


def show_cats():
    for headers in keys.MARKETYO_MARKET_HEADERS:
        print(headers.get("client"))
        MarketyoSpider.category_id_generator(headers)
        print("\n")


if __name__ == "__main__":
    debug_spider(MarketyoSpider)
