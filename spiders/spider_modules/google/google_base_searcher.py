import urllib.parse

import constants as keys
from spiders.spider_modules.base import BaseSpider
from spiders.test_spider import debug_spider


class GoogleSearcher(BaseSpider):
    def __init__(self, *args, **kwargs):
        super(GoogleSearcher, self).__init__(*args, base_domain="google.com")

    def parse(self, response):
        results = response.css(".sh-dlr__list-result")
        if not results:
            results = response.css(".g")

        hrefs = [res.css(" a::attr(href)").extract_first() for res in results]
        for href in hrefs:
            if "/shopping/product" in href:
                detail_url = urllib.parse.urljoin(self.base_url, href)
                detail_url = detail_url.split("?")[0]
                yield {keys.LINK: detail_url, keys.MARKET: keys.GOOGLE}


if __name__ == "__main__":
    debug_spider(GoogleSearcher)
