import scrapy

import constants as keys
from data_services import mark_out_of_stock
from spiders.spider_modules.base import BaseSpider
from spiders.spider_modules.visible.with_search.groseri_helper import TopLocalHelper
from spiders.test_spider import debug_spider


class TopLocalSpider(BaseSpider):
    name = keys.GROSERI

    def __init__(self, *args, **kwargs):
        super(TopLocalSpider, self).__init__(*args, base_domain="groseri.com.tr")
        self.start_urls = TopLocalHelper.get_category_urls(self.base_url)

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url, callback=self.parse, meta={"url": url, keys.PAGE_NUMBER: 1}
            )

    def parse(self, response):
        products = response.css(".urunler")
        if not products:
            return

        for product_div in products:
            product = TopLocalHelper.extract_product_info(product_div, self.base_url)
            if product:
                self.links_seen.add(product.get(keys.LINK))
                yield product

        page_number = response.meta.get(keys.PAGE_NUMBER, 1) + 1
        url = response.meta.get("url")
        next_page_url = url + "?page=%s" % page_number
        yield response.follow(
            next_page_url,
            callback=self.parse,
            meta={keys.PAGE_NUMBER: page_number, "url": url},
        )

    def close(self, reason):
        self.logger.info("Spider closed: %s due to %s", self.name, reason)
        if reason == "finished":
            mark_out_of_stock(self.links_seen, self.name)


if __name__ == "__main__":
    debug_spider(TopLocalSpider)
