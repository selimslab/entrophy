import scrapy

import constants as keys
from services.price.convert_price import convert_price
from services.get_soup import get_soup
from spiders.spider_modules.base import BaseSpider
from spiders.test_spider import debug_spider


class TopLocalSpider(BaseSpider):
    name = keys.ALTUNBILEK

    def __init__(self, *args, **kwargs):
        super(TopLocalSpider, self).__init__(
            *args, **kwargs, base_domain="altunbilekler.com"
        )

    @staticmethod
    def get_category_urls():
        url = "https://altunbilekler.com"
        soup = get_soup(url)
        nav = soup.find("ul", {"class": "HeaderMenu2"})
        lis = nav.findAll("li", recursive=False)
        hrefs = [li.find("a", href=True).get("href").strip() for li in lis]
        cat_urls = [url + href for href in hrefs]
        return cat_urls

    @staticmethod
    def extract_product_info(product_div, base_url):
        name = product_div.css(".productName a::text").extract_first().strip()

        price = product_div.css(".discountPrice span:first-child::text").extract_first()
        price = price.replace(".", "").replace(",", ".").replace("₺", "").strip()
        price = convert_price(price)
        if not price:
            return {}

        src = product_div.css(
            ".productImage a img::attr(data-original)"
        ).extract_first()
        href = product_div.css(".productImage a::attr(href)").extract_first()

        return {
            keys.LINK: base_url + href,
            keys.NAME: name,
            keys.SRC: base_url + src,
            keys.PRICE: price,
            keys.MARKET: keys.ALTUNBILEK,
            keys.OUT_OF_STOCK: False,
        }

    def start_requests(self):
        for category_url in self.get_category_urls():
            yield scrapy.Request(
                category_url, callback=self.parse, meta={"category_url": category_url}
            )

    def parse(self, response):
        table = response.css(".ProductList")
        products_div = table.css(".productItem")

        for product_div in products_div:
            product = self.extract_product_info(product_div, self.base_url)
            yield product

        next_page_href = response.css(
            ".pageBorder a:last-child::attr(href)"
        ).extract_first()

        if next_page_href and "sayfa" in next_page_href:
            category_url = response.meta.get("category_url")
            next_page_url = category_url + next_page_href
            yield response.follow(
                next_page_url, callback=self.parse, meta={"category_url": category_url}
            )


if __name__ == "__main__":
    debug_spider(TopLocalSpider)
    # print(TopLocalSpider.get_category_urls())
