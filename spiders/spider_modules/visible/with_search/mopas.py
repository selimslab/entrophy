import constants as keys
from spec.model.spider_config import SpiderConfig
from spiders.spider_modules.base import BaseSpider
from spiders.spider_modules.visible.with_search.mopas_helper import MopasHelper
from spiders.test_spider import debug_spider


class MopasSpider(BaseSpider):
    name = keys.MOPAS

    def __init__(self, *args, **kwargs):
        config = SpiderConfig(
            is_basic=True,
            name=self.name,
            base_domain="mopas.com.tr",
            category_function=MopasHelper.get_category_urls,
            extract_function=MopasHelper.extract_product_info,
            table_selector=".product-list-grid",
            product_selector=".card",
            next_page_href=".pagination-next a::attr(href)",
        )
        super().__init__(*args, **kwargs, config=config)


if __name__ == "__main__":
    debug_spider(MopasSpider)
