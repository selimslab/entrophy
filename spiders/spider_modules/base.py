import scrapy

import constants as keys
from data_services import mark_out_of_stock


class BaseSpider(scrapy.Spider):
    def __init__(self, *args, **kwargs):
        scrapy.Spider.__init__(self)

        self.config = kwargs.get("config")
        if self.config:
            self.base_domain = self.config.base_domain
            self.base_url = "https://www." + self.base_domain
            self.start_urls = self.config.category_function(self.base_url)

        else:
            self.base_domain = kwargs.get("base_domain")

        self.base_url = "https://www." + self.base_domain
        self.allowed_domains = [self.base_domain]

        self.next_page = True
        self.links_seen = set()

        self.debug = kwargs.get("debug", False)

    def parse(self, response):
        if self.config:
            table = response.css(self.config.table_selector)
            products_div = table.css(self.config.product_selector)

            for product_div in products_div:
                product = self.config.extract_function(product_div, self.base_url)
                self.links_seen.add(product.get(keys.LINK))
                yield product

            next_page_href = response.css(self.config.next_page_href).extract_first()

            if next_page_href:
                next_page_url = self.base_url + next_page_href
                yield response.follow(next_page_url, callback=self.parse)
        else:
            pass

    def close(self, reason):
        if self.config:
            self.logger.info("Spider closed: %s due to %s", self.name, reason)
            mark_out_of_stock(self.links_seen, self.name)
