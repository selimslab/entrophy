import re

import constants as keys
from data_services import mark_out_of_stock
from services.convert_price import convert_price
from services.get_soup import get_soup
from spiders.spider_modules.base import BaseSpider
from spiders.test_spider import debug_spider


class TopLocalHelper:
    @staticmethod
    def get_category_urls(url):
        soup = get_soup(url)
        lis = soup.findAll("a", {"class": "dMenu"})
        cat_urls = [li.get("href").strip() for li in lis if li]
        return cat_urls


class TopLocalSpider(BaseSpider):
    name = keys.SEYHANLAR

    def __init__(self, *args, **kwargs):
        super(TopLocalSpider, self).__init__(*args, base_domain="seyhanlar.com")
        self.start_urls = TopLocalHelper.get_category_urls(self.base_url)

    @staticmethod
    def extract_product_info(product_div):
        name = product_div.css(".product-name a::text").extract_first()
        name = " ".join(name.split())

        src = product_div.css("a.product-image img::attr(data-src)").extract_first()

        link = product_div.css("a.product-image::attr(href)").extract_first()

        product = {
            keys.LINK: link,
            keys.NAME: name,
            keys.SRC: src,
            keys.MARKET: keys.SEYHANLAR,
            keys.OUT_OF_STOCK: False,
        }

        # handle price
        price = product_div.css(".product-price strong::text").extract_first()
        if "." in price:
            price = price.split(".")[0]
        price = price.replace(",", ".").replace("TL", "").strip()
        if price == "Stokta Yok":
            product[keys.OUT_OF_STOCK] = True
        else:
            price = convert_price(price)
            if not price:
                return

        product[keys.PRICE] = price

        barcode = re.findall("[0-9]{13}", src)
        if not barcode:
            barcode = re.findall("[0-9]{14}", src)
        if barcode:
            product[keys.BARCODES] = barcode

        return product

    def parse(self, response):
        grid = response.css(".product-list")
        products = grid.css(".product-cart")

        for product_div in products:
            product = self.extract_product_info(product_div)
            if product:
                self.links_seen.add(product.get(keys.LINK))
                yield product

        next_page_url = response.css('a[rel="next"]::attr(href)').extract_first()
        if next_page_url:
            yield response.follow(next_page_url, callback=self.parse)

    def close(self, reason):
        self.logger.info("Spider closed: %s due to %s", self.name, reason)
        if reason == "finished":
            mark_out_of_stock(self.links_seen, self.name)


if __name__ == "__main__":
    debug_spider(TopLocalSpider)
