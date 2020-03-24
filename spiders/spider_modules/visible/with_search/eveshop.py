import constants as keys
from spiders.spider_modules.base import BaseSpider
from spiders.spider_modules.visible.with_search.eve_helper import EveHelper
from spiders.test_spider import debug_spider


class EveShopSpider(BaseSpider):
    name = keys.EVESHOP

    def __init__(self, *args, **kwargs):
        super(EveShopSpider, self).__init__(*args, base_domain="eveshop.com.tr")
        self.start_urls = EveHelper.get_category_urls(self.base_url)

    def parse(self, response):
        grid = response.css(".prd-list")
        products = grid.css(".product")

        for product in products:
            product_info = EveHelper.extract_product_info(product, self.base_url)
            if product_info:
                yield product_info

        if self.next_page:
            next_page_href = response.css(
                "a#ctl00_u14_ascUrunList_ascPagingDataAlt_lnkNext::attr(href)"
            ).extract_first()
            if next_page_href:
                next_page_url = self.base_url + next_page_href
                yield response.follow(next_page_url, callback=self.parse)


if __name__ == "__main__":
    debug_spider(EveShopSpider)
