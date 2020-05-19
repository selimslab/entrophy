import scrapy
from bs4 import BeautifulSoup

import constants as keys
from data_services import mark_out_of_stock
from spiders.spider_modules.base import BaseSpider
from spiders.test_spider import debug_spider


class N11Spider(BaseSpider):
    name = keys.N11

    def __init__(self, *args):
        super(N11Spider, self).__init__(*args, base_domain="n11.com")
        self.start_urls = {"/supermarket", "/kozmetik-kisisel-bakim"}

    # def start_requests(self):
    #     for url in self.start_urls:
    #         page_url = self.base_url + url
    #         yield scrapy.Request(
    #             page_url,
    #             callback=self.parse,
    #             meta={"url": page_url, keys.PAGE_NUMBER: 1},
    #         )
    #
    # def parse(self, response):
    #     html_body = BeautifulSoup(response.text, "html.parser")
    #     parsed_html = html_body.find("ul", class_="catalog-view clearfix products-container")
    #     products = parsed_html.findAll("a")
    #
    #     for product in products:
    #         product_name = product['title']
    #         url = product['href']
    #         src = product.find("img", class_="img-cont")['src']
    #         price_div = product.find("div", class_="gg-w-24 gg-d-24 gg-t-24 gg-m-24 padding-none product-price-info")
    #         price = (price_div.find("p")).text \
    #             .replace(".", "") \
    #             .replace(",", ".") \
    #             .replace("TL", "") \
    #             .strip()
    #         p = {
    #             keys.LINK: url,
    #             keys.NAME: product_name,
    #             keys.SRC: src,
    #             keys.PRICE: price,
    #             keys.MARKET: keys.GITTIGIFIYOR,
    #             keys.OUT_OF_STOCK: False,
    #         }
    #         self.links_seen.add(p.get(keys.LINK))
    #         yield p
    #
    #     self.next_page = self.check_next_page(response)
    #     if self.next_page:
    #         current_page_number = response.meta.get(keys.PAGE_NUMBER, 1)
    #         next_page_number = current_page_number + 1
    #         url = response.meta.get("url")
    #         next_page_url = url + "?sf=%s" % next_page_number
    #         yield response.follow(
    #             next_page_url,
    #             meta={
    #                 "url": url,
    #                 "next_page_url": next_page_url,
    #                 keys.PAGE_NUMBER: next_page_number,
    #             },
    #             callback=self.parse,
    #         )
    #
    # @staticmethod
    # def check_next_page(response):
    #     html_body = BeautifulSoup(response.text, "html.parser")
    #     footer = html_body.find("div", class_="pager pt30 hidden-m gg-d-24")
    #     pages = footer.findAll("li")
    #
    #     if "next-link" in pages[-1]['class']:
    #         next_page = True
    #     else:
    #         next_page = False
    #
    #     return next_page
    #
    # def close(self, reason):
    #     self.logger.info("Spider closed: %s due to %s", self.name, reason)
    #     mark_out_of_stock(self.links_seen, self.name)


if __name__ == "__main__":
    debug_spider(N11Spider)
