import json
import re

import scrapy

import constants as keys
from services.get_soup import get_soup
from spiders.spider_modules.base import BaseSpider
from spiders.test_spider import debug_spider


class TopLocalHelper:
    @staticmethod
    def get_category_urls(url):
        soup = get_soup(url)
        lis = soup.findAll("a", {"class": "megamain-cat"})
        cat_urls = [li.get("href").strip() for li in lis]
        cat_urls = [url for url in cat_urls if len(url) > 3]
        return cat_urls

    @staticmethod
    def extract(product_div, base_url):
        link = base_url + product_div.css("a::attr(href)").extract_first().strip()
        name = product_div.css(".description h4::text").extract_first().strip()
        src = product_div.css(".image-hover img::attr(data-src)").extract_first()
        if src:
            src = src.split("//")[1].strip()
            src = "https://" + src

        price = product_div.css(".price-sales::text").extract_first()
        if price:
            price = price.replace("TL", "")
            if "." in price:
                price = price.split(",")[0]
            else:
                price = price.replace(",", ".")
            price = float(price.strip())

        if not (price and name and src):
            return {}
        product = {
            keys.LINK: link,
            keys.NAME: name,
            keys.SRC: src,
            keys.PRICE: price,
            keys.MARKET: keys.CIVIL,
        }
        barcode = re.findall("[0-9]{13}", src)
        if not barcode:
            barcode = re.findall("[0-9]{14}", src)
        if barcode:
            product[keys.BARCODES] = barcode

        return product


class CivilSpider(BaseSpider):
    name = keys.CIVIL

    def __init__(self, *args, **kwargs):
        super(CivilSpider, self).__init__(*args, base_domain="civilim.com")

    def start_requests(self):
        cat_urls = TopLocalHelper.get_category_urls(self.base_url)
        for cat_url in cat_urls:
            cat_url = self.base_url + cat_url + "?type=json"
            yield scrapy.Request(cat_url, callback=self.parse)

    def parse(self, response):
        json_response = json.loads(response.body_as_unicode())
        html_content = json_response.get("response")
        resp = scrapy.Selector(text=html_content)
        products = resp.css(".listitem")

        for product_div in products:
            product = TopLocalHelper.extract(product_div, self.base_url)
            if product:
                yield product

        next_data_url = json_response.get("next_data_url")
        if next_data_url:
            yield response.follow(self.base_url + next_data_url, callback=self.parse)


if __name__ == "__main__":
    debug_spider(CivilSpider)
