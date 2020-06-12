import re
import scrapy

import constants as keys
from services.convert_price import convert_price
from services.get_soup import get_soup
from spiders.spider_modules.base import BaseSpider
from spiders.test_spider import debug_spider


class TopLocalHelper:
    @staticmethod
    def get_category_urls(url):
        soup = get_soup(url)
        lis = soup.findAll("li", {"class": "with-sub-menu"})
        hrefs = [li.find("a", href=True).get("href").strip() for li in lis]
        cat_urls = [url + href for href in hrefs]
        return cat_urls


class TopLocalSpider(BaseSpider):
    name = keys.PEYNIRCIBABA

    def __init__(self, *args, **kwargs):
        super(TopLocalSpider, self).__init__(
            *args, **kwargs, base_domain="peynircibaba.com"
        )
        self.start_urls = TopLocalHelper.get_category_urls(self.base_url)

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url, callback=self.parse, meta={"url": url, keys.PAGE_NUMBER: 1}
            )

    @staticmethod
    def extract_product_info(product_div):
        name = product_div.css(".product-name::text").extract_first().strip()

        # handle price
        price = product_div.css(".price::text").extract_first()

        price = price.replace(",", ".").replace("TL", "").strip()
        price = convert_price(price)
        if not price:
            return

        src = product_div.css(".product-image img::attr(src)").extract_first()

        link = product_div.css(".product-image a::attr(href)").extract_first()

        product = {
            keys.LINK: link,
            keys.NAME: name,
            keys.SRC: src,
            keys.PRICE: price,
            keys.MARKET: keys.PEYNIRCIBABA,
        }

        barcode = re.findall("[0-9]{13}", src)
        if not barcode:
            barcode = re.findall("[0-9]{14}", src)
        if barcode:
            product[keys.BARCODES] = barcode

        return product

    def parse(self, response):
        grid = response.css(".product-list")
        if not grid:
            return

        products = grid.css(".one-product")

        for product_div in products:
            product = self.extract_product_info(product_div)
            if product:
                self.links_seen.add(product.get(keys.LINK))
                yield product

        page_number = response.meta.get(keys.PAGE_NUMBER, 1) + 1
        url = response.meta.get("url")
        next_page_url = url + "?sayfa=%s" % page_number
        yield response.follow(
            next_page_url,
            callback=self.parse,
            meta={keys.PAGE_NUMBER: page_number, "url": url},
        )


if __name__ == "__main__":
    debug_spider(TopLocalSpider)
