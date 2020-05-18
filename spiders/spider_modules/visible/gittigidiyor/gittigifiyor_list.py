import scrapy

import constants as keys
from data_services import mark_out_of_stock
from spiders.spider_modules.base import BaseSpider
from spiders.spider_modules.visible.with_search.a101_helper import A101Helper
from spiders.test_spider import debug_spider


class GittigidiyorSpider(BaseSpider):
    name = keys.A101

    def __init__(self, *args, **kwargs):
        super(GittigidiyorSpider, self).__init__(*args, base_domain="gittigidiyor.com/")
        if kwargs.get("debug"):
            print('yes')
            self.start_urls = {"/kozmetik-kisisel-bakim/sampuan/"}
        else:
            print('no')

            self.start_urls = A101Helper.get_category_urls()

    # def start_requests(self):
    #     for url in self.start_urls:
    #         page_url = self.base_url + url
    #         yield scrapy.Request(
    #             page_url,
    #             callback=self.parse,
    #             meta={"url": page_url, keys.PAGE_NUMBER: 1},
    #         )
    #
    # def parse(self, response):
    #     table = response.css(".product-list-general")
    #     products = table.css(".set-product-item")
    #
    #     for product_div in products:
    #         product = A101Helper.extract_product_info(product_div, self.base_url)
    #         if product:
    #             self.links_seen.add(product.get(keys.LINK))
    #             yield product
    #
    #     if self.next_page:
    #         current_page_number = response.meta.get(keys.PAGE_NUMBER, 1)
    #         next_page_number = current_page_number + 1
    #         max_page_number = self.get_max_page_number(response)
    #
    #         if next_page_number <= max_page_number:
    #             url = response.meta.get("url")
    #             next_page_url = url + "?page=%s" % next_page_number
    #             yield response.follow(
    #                 next_page_url,
    #                 meta={
    #                     "url": url,
    #                     "next_page_url": next_page_url,
    #                     keys.PAGE_NUMBER: next_page_number,
    #                 },
    #                 callback=self.parse,
    #             )
    #
    # @staticmethod
    # def get_max_page_number(response):
    #     nav_items = response.css(".pagination").css("ul li")
    #     page_numbers = list()
    #     for nav in nav_items:
    #         num = nav.css(".page-link::text").extract_first()
    #         try:
    #             page_numbers.append(int(num))
    #         except ValueError:
    #             continue
    #
    #     if page_numbers:
    #         max_page_number = max(page_numbers)
    #     else:
    #         max_page_number = 1
    #
    #     return max_page_number
    #
    # def close(self, reason):
    #     self.logger.info("Spider closed: %s due to %s", self.name, reason)
    #     mark_out_of_stock(self.links_seen, self.name)


if __name__ == "__main__":
    debug_spider(GittigidiyorSpider)
