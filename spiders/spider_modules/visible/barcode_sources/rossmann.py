import bs4
import requests

import constants as keys
from data_services import mark_out_of_stock
from services.convertor import convert_price
from spiders.spider_modules.base import BaseSpider
from spiders.test_spider import debug_spider


class RossmannHelper:
    @staticmethod
    def get_category_urls(url):
        r = requests.get(url)
        soup = bs4.BeautifulSoup(r.content, features="lxml")
        links = soup.findAll("li", {"class": "mega-dropdown"})
        cat_urls = []
        for link in links[:-1]:
            a = link.find("a", href=True)
            href = a.get("href")
            cat_url = url + href
            cat_urls.append(cat_url)

        return cat_urls


class RossmannSpider(BaseSpider):
    name = keys.ROSSMANN

    def __init__(self, *args, **kwargs):
        super(RossmannSpider, self).__init__(*args, base_domain="rossmann.com.tr")
        if self.debug:
            self.start_urls = ["https://www.rossmann.com.tr/erkek-parfum/"]
        else:
            self.start_urls = RossmannHelper.get_category_urls(self.base_url)

    def parse(self, response):
        grid = response.css(".products-grid")
        products = grid.css(".item.saleable")  # all in stock

        for product in products:
            product_info = extract_product_info(product)
            if product_info:
                self.links_seen.add(product_info.get(keys.LINK))
                yield product_info

        out_of_stock_products = grid.css(".item.not-saleable")
        for product in out_of_stock_products:
            product_info = extract_product_info(product)
            if product_info:
                product_info[keys.OUT_OF_STOCK] = True
                yield product_info

        if self.next_page:
            next_page_url = response.css("a.next-grey::attr(href)").extract_first()
            if next_page_url:
                yield response.follow(next_page_url, callback=self.parse)

    def close(self, reason):
        self.logger.info("Spider closed: %s due to %s", self.name, reason)
        mark_out_of_stock(self.links_seen, self.name)


def extract_product_info(product):
    brand = product.css(".product-brand::text").extract_first()
    if brand:
        brand = brand.strip()

    name = product.css(".product-name a::text").extract_first()
    name2 = product.css(".product-name.name2 a::text").extract_first()
    size = product.css(".product-name.freight a::text").extract_first()

    name_parts = [brand, name, name2]
    if size and name and size not in name:
        name_parts.append(size)
    name_parts = [n.strip() for n in name_parts if n]
    name = " ".join(name_parts)
    name = " ".join(name.split())

    price = product.css(".price::text")[-1].extract().replace("₺", "").strip()
    price = price.replace(".", "").replace(",", ".")
    price = convert_price(price)
    if not price:
        return

    link = product.css("a.product-image::attr(href)").extract_first()
    src = product.css("a.product-image img::attr(data-src)").extract_first().strip()
    barcode = src.split("/")[-1].split("_")[0]

    return {
        keys.LINK: link,
        keys.NAME: name,
        keys.SRC: src,
        keys.PRICE: price,
        keys.MARKET: keys.ROSSMANN,
        keys.BARCODES: [barcode],
        keys.SIZE: size,
        keys.BRAND: brand,
        keys.OUT_OF_STOCK: False,
    }


if __name__ == "__main__":
    debug_spider(RossmannSpider)
