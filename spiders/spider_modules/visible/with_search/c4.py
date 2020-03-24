import constants as keys
from data_services import mark_out_of_stock
from spiders.spider_modules.base import BaseSpider
from spiders.spider_modules.visible.with_search.c4_helper import CarrefourHelper
from spiders.test_spider import debug_spider


class CarrefourSpider(BaseSpider):
    name = keys.CARREFOUR

    def __init__(self, *args, **kwargs):
        super(CarrefourSpider, self).__init__(
            *args, **kwargs, base_domain="carrefoursa.com"
        )
        if kwargs.get("debug"):
            self.start_urls = ["https://www.carrefoursa.com/tr/gida-sekerleme/c/1110"]
        else:
            self.start_urls = CarrefourHelper.get_category_urls(self.base_url)

    def close(self, reason):
        self.logger.info("Spider closed: %s due to %s", self.name, reason)
        if reason == "finished":
            mark_out_of_stock(self.links_seen, self.name)

    def parse(self, response):
        table = response.css("ul.product-listing")
        products_div = table.css("div.product-card")

        for product_div in products_div:
            product = CarrefourHelper.extract_product_info(product_div, self.base_url)
            self.links_seen.add(product.get(keys.LINK))
            yield product

        next_page_href = response.css(".pr-next::attr(href)").extract_first()
        if next_page_href:
            next_page_url = self.base_url + next_page_href
            yield response.follow(
                next_page_url, meta={"url": next_page_url}, callback=self.parse
            )


if __name__ == "__main__":
    debug_spider(CarrefourSpider)
