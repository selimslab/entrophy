import json
import re
from pprint import pprint

import scrapy

import constants as keys
from spiders.spider_modules.base import BaseSpider
from spiders.spider_modules.search_helper import (
    CUSTOM_SEARCHBOX_SETTINGS,
    BarcodeSearchHelper,
)


class EveShopSearcher(BaseSpider):
    name = "search_eve"
    custom_settings = CUSTOM_SEARCHBOX_SETTINGS

    def __init__(self, *args, **kwargs):
        barcodes_to_search = BarcodeSearchHelper.get_barcodes_to_search(
            keys.EVESHOP, keys.COSMETICS_MARKETS
        )
        self.barcode_generator = BarcodeSearchHelper.barcode_generator(
            barcodes_to_search
        )
        super(EveShopSearcher, self).__init__(*args, base_domain="eveshop.com.tr")

    def start_requests(self):
        base = "https://www.eveshop.com.tr/userControls/kutu/ascArama_ajx.aspx?searchType=0&suggType=2&srt=ES&lang=tr-TR&text="

        for barcode in self.barcode_generator:
            url = base + barcode
            yield scrapy.Request(
                url, callback=self.parse, meta={keys.BARCODES: barcode}
            )

    @staticmethod
    def extract_product_json(response):
        search_results = response.css("::text").extract()
        search_results = " ".join(search_results)
        products_match = re.findall(r"\"products\":\[(.*?)\]", search_results)

        if not products_match:
            return

        products_str = products_match.pop()

        if not products_str:
            return

        product_json = json.loads(products_str)
        return product_json

    @staticmethod
    def extract_product_info(product_json, base_url):
        pprint(product_json)
        href = product_json.get("productUrl", "")
        name = product_json.get("productName", "")
        price = product_json.get("productSalesPrice", "")

        if not (href and price and name):
            return

        res = dict()

        link = base_url + href
        res[keys.LINK] = link

        """
        brand = link.split("/")[3].strip().replace("-", " ")
        print(brand)
        if brand.lower() not in name.lower():
            name = " ".join([brand, name]).title()
    
        """
        res[keys.NAME] = name

        price = (
            price.replace("TL", "")
            .strip()
            .replace(".", "")
            .replace(",", ".")
            .replace(" ", "")
        )

        try:
            res[keys.PRICE] = float(price)
        except TypeError as e:
            print(e)

        return res

    @staticmethod
    def get_product(response, base_url, market_name):
        product_json = EveShopSearcher.extract_product_json(response)
        if product_json:
            result = EveShopSearcher.extract_product_info(product_json, base_url)
            if result:
                result[keys.BARCODES] = response.meta.get(keys.BARCODES)
                result[keys.MARKET] = market_name
                return result

    def parse(self, response):
        product = self.get_product(response, self.base_url, keys.EVESHOP)
        if product:
            yield product
