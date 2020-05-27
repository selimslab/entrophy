# -*- coding: utf-8 -*-
from spiders.spider_modules.base import BaseSpider
from spiders.test_spider import debug_spider
import json
import bs4
from pprint import pprint
import constants as keys
import data_services.mongo.collections as collections


class TrendyolDetailSpider(BaseSpider):
    name = "ty_detail"
    custom_settings = {
        "CLOSESPIDER_TIMEOUT": 0,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, base_domain="trendyol.com")
        if self.debug:
            self.start_urls = [
                "https://www.trendyol.com/puma/acsent-erkek-gunluk-spor-ayakkabi-37131304-p-34722085?boutiqueId=481141&merchantId=109687",
                "https://www.trendyol.com/l-oreal-paris/nem-terapisi-aloe-vera-suyu-kuru-ve-hassas-ciltler-icin-su-bazli-gunluk-bakim-p-2279199",
            ]
        else:
            self.start_urls = collections.items_collection.distinct(
                keys.LINK, {keys.MARKET: "ty", keys.BARCODES: {"$exists": False}}
            )

        self.instant_update_active = False

    def parse(self, response):
        soup = bs4.BeautifulSoup(response.text, features="html.parser")
        script_tags = soup.findAll("script", type="application/ld+json", text=True)
        for script_tag in script_tags:
            s = script_tag.string
            product = json.loads(s)
            pprint(product)
            if '"@type": "Product"' in s:
                product = json.loads(s)
                pprint(product)
                product[keys.BARCODES] = product.pop("gtin13", [])
                product[keys.LINK] = product.pop("url", "")
                product[keys.BRAND] = product.get("brand", {}).get("name")
                yield product


if __name__ == "__main__":
    debug_spider(TrendyolDetailSpider)
