import requests
import scrapy
from bs4 import BeautifulSoup

import constants as keys
from data_services import mark_out_of_stock
from spiders.spider_modules.base import BaseSpider
from spiders.test_spider import debug_spider


class N11Spider(BaseSpider):
    name = keys.N11

    def __init__(self, *args, **kwargs):
        super(N11Spider, self).__init__(*args, base_domain="n11.com")
        self.start_urls = ['/supermarket'] + self.get_kozmetik_kisisel_bakim_urls(base_domain=self.base_url)

    def get_kozmetik_kisisel_bakim_urls(self, base_domain):
        categories_url = list()
        response = requests.get(base_domain)
        html_body = BeautifulSoup(response.text, "html.parser")
        parsed_html = html_body.findAll("li", class_="catMenuItem")
        category = ''
        for category_div in parsed_html:
            category = category_div.find('a')
            if "kozmetik" in category.text.lower():
                category = category_div
                break
        for subcategory in category.findAll("li", class_="subCatMenuItem"):
            categories_url.append('/' + ((subcategory.find('a')['href']).split('/'))[-1])

        return categories_url

    def start_requests(self):
        for url in self.start_urls:
            page_url = self.base_url + url
            yield scrapy.Request(
                page_url,
                callback=self.parse,
                meta={"url": page_url, keys.PAGE_NUMBER: 1},
            )

    def parse(self, response):
        html_body = BeautifulSoup(str(response.text), "html.parser")
        parsed_detail = html_body.findAll("div", class_="pro")
        parsed_price = html_body.findAll("ins")
        for product_div, price in zip(parsed_detail, parsed_price):
            product = product_div.find('a')
            product_name = product['title']
            url = product['href']
            src = product_div.find("img")['data-original']
            price = price.text \
                .replace(".", "") \
                .replace(",", ".") \
                .replace("TL", "") \
                .strip()
            p = {
                keys.LINK: url,
                keys.NAME: product_name,
                keys.SRC: src,
                keys.PRICE: price,
                keys.MARKET: keys.N11,
                keys.OUT_OF_STOCK: False,
            }
            self.links_seen.add(p.get(keys.LINK))
            yield p

        self.next_page = self.check_next_page(response)
        if self.next_page:
            current_page_number = response.meta.get(keys.PAGE_NUMBER, 1)
            next_page_number = current_page_number + 1
            url = response.meta.get("url")
            next_page_url = url + "?pg=%s" % next_page_number
            yield response.follow(
                next_page_url,
                meta={
                    "url": url,
                    "next_page_url": next_page_url,
                    keys.PAGE_NUMBER: next_page_number,
                },
                callback=self.parse,
            )

    @staticmethod
    def check_next_page(response):
        html_body = BeautifulSoup(response.text, "html.parser")
        footer = html_body.find("div", class_="pagination")
        pages = footer.findAll("a")

        if "nextBlock" in pages[-1]['class']:
            next_page = True
        else:
            next_page = False

        return next_page

    def close(self, reason):
        self.logger.info("Spider closed: %s due to %s", self.name, reason)
        mark_out_of_stock(self.links_seen, self.name)


if __name__ == "__main__":
    debug_spider(N11Spider)
