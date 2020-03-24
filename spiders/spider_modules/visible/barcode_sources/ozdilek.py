import re

import scrapy

import constants as keys
from services.convertor import convert_price
from services.get_soup import get_soup
from spiders.spider_modules.base import BaseSpider
from spiders.test_spider import debug_spider


class TopLocalHelper:
    @staticmethod
    def get_category_ids():
        url = "https://ozdilekteyim.com/shop/tr/bursahipermarket/"
        soup = get_soup(url)
        lis = soup.findAll("div", {"class": "child-menu"})
        cat_ids = [li.find("a", href=True).get("id").strip() for li in lis]
        cat_ids = [id.split("_")[-1] for id in cat_ids]
        return cat_ids


class TopLocalSpider(BaseSpider):
    name = keys.OZDILEK

    def __init__(self, *args, **kwargs):
        super(TopLocalSpider, self).__init__(*args, base_domain="ozdilekteyim.com")

    def start_requests(self):
        base = "https://www.ozdilekteyim.com/shop/OHProductListingView?&resultsPerPage=36&storeId=10153&categoryId="
        for id in TopLocalHelper.get_category_ids():
            url = base + id
            yield scrapy.Request(
                url,
                callback=self.parse,
                meta={"base_page_url": url, keys.PAGE_NUMBER: 0},
            )

    @staticmethod
    def extract_product_info(product_div, replace_url):
        info = product_div.css(".product_info")

        name = info.css(".product_name a::text").extract_first()

        price_div = info.css(".price")
        pri = price_div.css(".etr-cur-pri::text").extract_first()
        decimal = price_div.css(".etr-cur-dec::text").extract_first()
        price = pri + decimal
        price = price.replace(",", ".")
        price = convert_price(price)
        if not price:
            return

        link = (
            product_div.css(".product-card-image::attr(href)")
            .extract_first()
            .replace(replace_url, "")
        )
        # link = "https://www.ozdilekteyim.com/shop/tr/ozdilekteyim/" + href

        src = product_div.css(".product-card-image img::attr(src)").extract_first()

        product = {
            keys.LINK: link,
            keys.NAME: name,
            keys.SRC: src,
            keys.PRICE: price,
            keys.MARKET: keys.OZDILEK,
        }
        barcode = re.findall("[0-9]{13}", src)
        if not barcode:
            barcode = re.findall("[0-9]{14}", src)
        if barcode:
            product[keys.BARCODES] = barcode

        return product

    def parse(self, response):

        grid = response.css(".grid")
        product_divs = grid.css(".product")
        replace_url = "http://www.ozdilekteyim.com/shop/tr/bursahipermarket/"
        for product_div in product_divs:
            product = self.extract_product_info(product_div, replace_url)
            if product:
                yield product

        nump = response.css(".num_products::text").extract_first()
        if nump:
            nump = nump.split("/")[1]
            nump = re.findall(r"\d+", nump)
            nump = int(nump.pop())

        page_number = response.meta.get(keys.PAGE_NUMBER, 0) + 1
        index = page_number * 36

        if nump and index < nump:
            base_page_url = response.meta.get("base_page_url")

            yield scrapy.FormRequest(
                base_page_url,
                meta={"base_page_url": base_page_url, keys.PAGE_NUMBER: page_number},
                callback=self.parse,
                formdata={"beginIndex": str(index)},
            )


if __name__ == "__main__":
    debug_spider(TopLocalSpider)
