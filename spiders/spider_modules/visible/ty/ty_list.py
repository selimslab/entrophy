# -*- coding: utf-8 -*-
from json import JSONDecodeError

import scrapy

from spiders.spider_modules.base import BaseSpider
from spiders.test_spider import debug_spider
import json
import bs4
import requests
from pprint import pprint
import constants as keys


class TrendyolSpider(BaseSpider):
    name = "ty"
    TRENDYOL_API = "https://api.trendyol.com/websearchgw/api/infinite-scroll%s?pi=%d&storefrontId=1&culture=tr-TR&userGenderId=2&searchStrategyType=DEFAULT&pId=ILKx9K99Gg&scoringAlgorithmId=3&categoryRelevancyEnabled=undefined&legalRequirement=True"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, base_domain="trendyol.com")
        self.start_urls = self.get_links_to_crawl()

    @staticmethod
    def get_links_to_crawl():
        r = requests.get("https://www.trendyol.com")
        soup = bs4.BeautifulSoup(r.content, "html.parser")
        nav = soup.find("ul", {"class": "main-nav"})
        link = dict()

        for menu in nav.findAll("li", class_="tab-link"):
            menu_title = menu.find("a", class_="category-header").text
            if "SÜPERMARKET" in menu_title or "KOZMETİK" in menu_title:
                categories = menu.findAll("div", class_="category-box")
                for category in categories:
                    submenu = category.find("a")
                    link[submenu.text] = submenu.get("href")
        return link

    def start_requests(self):
        links = self.get_links_to_crawl()
        for _, url in links.items():
            page = 1
            page_url = f"https://api.trendyol.com/websearchgw/api/infinite-scroll{url}?pi={page}&storefrontId=1&culture=tr-TR&userGenderId=2&searchStrategyType=DEFAULT&pId=ILKx9K99Gg&scoringAlgorithmId=3&categoryRelevancyEnabled=undefined&legalRequirement=True"
            yield scrapy.Request(
                page_url,
                callback=self.parse,
                meta={"url": url, keys.PAGE_NUMBER: 1},
            )

    def parse(self, response):
        parsed_json = json.loads(response.body, strict=False)
        products = parsed_json.get("result", {}).get("products")
        url = response.meta.get('url')

        current_page_number = response.meta.get(keys.PAGE_NUMBER, 1)
        next_page = current_page_number + 1

        next_page_url = f"https://api.trendyol.com/websearchgw/api/infinite-scroll{url}?pi={next_page}&storefrontId=1&culture=tr-TR&userGenderId=2&searchStrategyType=DEFAULT&pId=ILKx9K99Gg&scoringAlgorithmId=3&categoryRelevancyEnabled=undefined&legalRequirement=True"

        keys_parse = {
            "name",
            "images",
            "installmentCount",
            "url",
            "tax",
            "ratingScore",
            "brand",
            "categoryHierarchy",
            "price",
            "promotions",
            "rushDeliveryDuration",
            "freeCargo",
        }

        for product in products:
            product = {k: v for k, v in product.items() if k in keys_parse}
            pprint(product)
            yield product

        try:
            r = requests.get(next_page_url).text
            json.loads(r, strict=False)
            next_page = True
        except JSONDecodeError:
            next_page = False

        if next_page:
            yield response.follow(
                next_page_url,
                meta={
                    "url": url,
                    "next_page_url": next_page_url,
                    keys.PAGE_NUMBER: next_page,
                },
                callback=self.parse,
            )


if __name__ == "__main__":
    debug_spider(TrendyolSpider)
