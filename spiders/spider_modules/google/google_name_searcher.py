from urllib.parse import quote_plus

import scrapy

import constants as keys
import data_services.mongo.collections as collections
from spiders.spider_modules.google.google_base_searcher import GoogleSearcher
from spiders.spider_modules.google.google_settings import GOOGLE_SETTINGS
from spiders.test_spider import debug_spider


class GoogleNameSearcher(GoogleSearcher):
    """
    Search names in google and save links to the detail pages
    """

    name = "google_name_search"
    custom_settings = GOOGLE_SETTINGS

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.debug = kwargs.get("debug")
        if self.debug:
            self.names_to_search = ["içim Labne Peynir 400 G"]
        else:
            self.names_to_search = collections.items_collection.distinct(
                keys.NAME, {keys.MARKET: keys.MIGROS}
            )

    def start_requests(self):
        base_search_url = self.base_url + "/search?tbm=shop&q="
        for name in self.names_to_search:
            search_url = base_search_url + quote_plus(name)
            yield scrapy.Request(search_url, callback=self.parse)


if __name__ == "__main__":
    debug_spider(GoogleNameSearcher)
