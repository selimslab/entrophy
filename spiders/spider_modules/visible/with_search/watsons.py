import constants as keys
from data_models.spider_config import SpiderConfig
from spiders.spider_modules.base import BaseSpider
from spiders.spider_modules.visible.with_search.watsons_helper import WatsonsHelper
from spiders.test_spider import debug_spider


class WatsonsSpider(BaseSpider):
    name = keys.WATSONS

    def __init__(self, *args, **kwargs):
        config = SpiderConfig(
            is_basic=True,
            name=self.name,
            base_domain="watsons.com.tr",
            category_function=WatsonsHelper.get_category_urls,
            extract_function=WatsonsHelper.extract_product_info,
            table_selector=".product-list-inner-container",
            product_selector=".product-box-container",
            next_page_href=".next-page a::attr(href)",
        )
        super().__init__(*args, **kwargs, config=config)


if __name__ == "__main__":
    debug_spider(WatsonsSpider)
