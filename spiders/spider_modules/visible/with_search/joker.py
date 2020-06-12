import constants as keys
from services.convert_price import convert_price
from services.get_soup import get_soup
from spiders.spider_modules.base import BaseSpider
from spiders.test_spider import debug_spider
import logging


class TopLocalHelper:
    @staticmethod
    def get_category_urls(url):
        soup = get_soup(url)
        lis = soup.findAll("li", {"class": "dropdown-submenu"})
        hrefs = [li.find("a", href=True).get("href").strip() for li in lis]
        cat_urls = [url + href for href in hrefs]
        logging.info(cat_urls)
        return cat_urls

    @staticmethod
    def get_categories(url):
        soup = get_soup(url)
        categories = dict()
        categories["category"] = []
        soup = soup.findAll(
            "ul",
            class_="dropdown-menu first-parent dress-special-menu mother-baby-nav-menu",
        )
        for submenu in soup:
            for category in submenu.findAll("li"):
                if not category.get("class"):
                    categories["category"].append(
                        (category.find("a").text).replace("|", "").strip()
                    )
        return categories

    @staticmethod
    def extract_product_info(product_div, base_url):
        name = product_div.css(".product-title span::text").extract_first()
        price = product_div.css(".discount-price::text").extract_first()
        price = (
            price.replace("TL", "")
            .replace(".", "")
            .replace(",", ".")
            .replace(" ", "")
            .strip()
        )
        price = convert_price(price)
        if not price:
            return

        src = product_div.css("meta::attr(content)").extract_first()
        hrefs = product_div.css("a::attr(href)").extract()
        link = ""
        for href in hrefs:
            if "script" not in href:
                link = base_url + href
                break

        product = {
            keys.LINK: link,
            keys.NAME: name,
            keys.SRC: src,
            keys.PRICE: price,
            keys.MARKET: keys.JOKER,
        }

        if product_div.css("#stoktayok"):
            product[keys.OUT_OF_STOCK] = True

        return product


class JokerCollector(BaseSpider):
    name = keys.JOKER

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, base_domain="joker.com.tr")
        self.start_urls = TopLocalHelper.get_category_urls(self.base_url)
        if kwargs.get("debug"):
            self.start_urls = ["https://www.joker.com.tr/arama"]

    def parse(self, response):
        grid = response.css(".j-product-list")
        products = grid.css(".item.product")

        for product_div in products:
            product = TopLocalHelper.extract_product_info(product_div, self.base_url)
            if product:
                yield product

        next_page_href = response.css(
            "li.last-pagination a::attr(href)"
        ).extract_first()
        if next_page_href:
            _, page = next_page_href.split("#&")
            next_page_url = "https://www.joker.com.tr/arama/?" + page
            yield response.follow(next_page_url, callback=self.parse)


if __name__ == "__main__":
    debug_spider(JokerCollector)
