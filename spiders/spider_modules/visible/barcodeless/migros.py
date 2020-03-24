import scrapy

import constants as keys
from data_services import mark_out_of_stock
from spiders.spider_modules.base import BaseSpider
from spiders.spider_modules.visible.barcodeless.migros_helper import MigrosHelper


class MigrosSpider(BaseSpider):
    name = keys.MIGROS

    def __init__(self, *args, **kwargs):
        super(MigrosSpider, self).__init__(*args, base_domain="migros.com.tr")

    def close(self, reason):
        self.logger.info("Spider closed: %s due to %s", self.name, reason)
        if reason == "finished":
            mark_out_of_stock(self.links_seen, self.name)

    def start_requests(self):
        for url in MigrosHelper.get_urls_migros(self.base_url):
            yield scrapy.Request(
                url, callback=self.parse, meta={"url": url, keys.PAGE_NUMBER: 1}
            )

    def parse(self, response):
        table = response.css("div.sub-category-product-list")
        products_div = table.css("div.product-card")

        for product_div in products_div:
            product = MigrosHelper.extract_product_info(product_div, self.base_url)
            self.links_seen.add(product.get(keys.LINK))
            yield product

        url = response.meta.get("url")
        if self.next_page:
            next_page_number = response.css(
                "li.pag-next a::attr(data-page)"
            ).extract_first()
            if next_page_number:
                page_number = response.meta.get(keys.PAGE_NUMBER, 1) + 1
                next_page_url = url + "?sayfa=%s" % page_number

                yield response.follow(
                    next_page_url,
                    callback=self.parse,
                    meta={keys.PAGE_NUMBER: page_number, "url": url},
                )
