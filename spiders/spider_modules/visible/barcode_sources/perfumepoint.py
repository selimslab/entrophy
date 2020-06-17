import re

import constants as keys
from data_services import mark_out_of_stock
from services.string.convert_price import convert_price
from services.get_soup import get_soup
from spiders.spider_modules.base import BaseSpider
from spiders.test_spider import debug_spider


class TopLocalHelper:
    @staticmethod
    def get_category_urls(url):
        soup = get_soup(url)
        nav = soup.find("div", {"class": "dropMenu"})
        ul = nav.find("ul")
        lis = ul.findAll("li", recursive=False)
        hrefs = [li.find("a", href=True).get("href").strip() for li in lis]
        cat_urls = [url + href for href in hrefs]
        return cat_urls


class TopLocalSpider(BaseSpider):
    name = keys.PERFUMEPOINT

    def __init__(self, *args, **kwargs):
        super(TopLocalSpider, self).__init__(*args, base_domain="perfumepoint.com.tr")
        self.start_urls = TopLocalHelper.get_category_urls(self.base_url)
        self.base_url = "http://www." + self.base_domain

    @staticmethod
    def extract_product_info(product_div, base_url):
        name = product_div.css(".showcaseTitle a::text").extract_first()
        name = " ".join(name.split())

        # handle price
        price = product_div.css(".showcasePriceTwo::text").extract_first()
        if "." in price:
            price = price.split(".")[0]
        price = price.replace(",", ".").replace("TL", "").strip()
        price = convert_price(price)
        if not price:
            return

        src = product_div.css(".showcasePicture img::attr(src)").extract_first()
        src = "https:" + src

        href = product_div.css(".showcasePicture a::attr(href)").extract_first()

        product = {
            keys.LINK: base_url + href,
            keys.NAME: name,
            keys.SRC: src,
            keys.PRICE: price,
            keys.MARKET: keys.PERFUMEPOINT,
        }

        barcode = re.findall("[0-9]{13}", src)
        if not barcode:
            barcode = re.findall("[0-9]{14}", src)
        if barcode:
            product[keys.BARCODES] = barcode

        return product

    def parse(self, response):
        grid = response.css(".ShowcaseContainer")
        products = grid.css(".showcase")

        for product_div in products:
            product = self.extract_product_info(product_div, self.base_url)
            if product:
                self.links_seen.add(product.get(keys.LINK))
                yield product

        next_page_href = response.css("._paginateRight a::attr(href)").extract_first()
        if next_page_href:
            next_page_url = self.base_url + next_page_href
            yield response.follow(next_page_url, callback=self.parse)

    def close(self, reason):
        self.logger.info("Spider closed: %s due to %s", self.name, reason)
        if reason == "finished":
            mark_out_of_stock(self.links_seen, self.name)


if __name__ == "__main__":
    debug_spider(TopLocalSpider)
