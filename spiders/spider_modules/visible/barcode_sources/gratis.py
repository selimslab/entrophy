import json

import requests
import scrapy

import constants as keys
from services.barcode_cleaner import BarcodeCleaner
from spiders.spider_modules.base import BaseSpider
from spiders.test_spider import debug_spider


class GratisHelper:
    @staticmethod
    def get_category_urls(base_url):
        api_url = base_url + "/ccstoreui/v1/"

        category_api_sub_url = "collections?categoryIds=501%2C502%2C503%2C505%2C504%2C506%2C507%2C508%2C509%2C510%2C511&fields=displayName%2Cid%2CdimensionId"
        category_url = api_url + category_api_sub_url
        r = requests.get(category_url)
        data = json.loads(r.content)

        categories = data.get("items")

        items_per_page = 18
        all_urls = list()

        for cat in categories:
            dimensionId = cat.get("dimensionId")
            if not dimensionId:
                continue
            sub_url = "search?N=" + dimensionId
            url_filter = "&Nr=AND(product.active:1,NOT(sku.listPrice:0.000000))"
            cat_url = api_url + sub_url + url_filter
            cat["base_url"] = cat_url

            r = requests.get(cat_url)
            data = json.loads(r.content)
            results = data.get("resultsList")
            count = results.get("totalNumRecs")

            cat["count"] = count
            urls = list()

            offset = 0
            while offset < count:
                page_params = "&Nrpp=" + str(items_per_page) + "&No=" + str(offset)
                page_url = cat_url + page_params
                urls.append(page_url)
                offset += items_per_page

            all_urls += urls

        return all_urls

    @staticmethod
    def get_gratis_discounted_prices(ids):
        url = "https://www.gratis.com/ccstoreui/v1/skus?fields=repositoryId%2ClistPrices&skuIds="
        for id in ids:
            url += str(id) + ","
        r = requests.get(url)
        data = json.loads(r.content)
        discs = dict()
        items = data.get("items", {})
        if not items:
            return discs
        for item in items:
            id = item.get("repositoryId")
            price = item.get("listPrices").get("loyaltyTurkeyPriceGroup")
            if price:
                discs[id] = round(float(price), 2)
        return discs


class GratisSpider(BaseSpider):
    name = keys.GRATIS

    def __init__(self, *args, **kwargs):
        super(GratisSpider, self).__init__(*args, **kwargs, base_domain="gratis.com")

        self.search_url = (
            "https://www.gratis.com/ccstoreui/v1/search?Nr=product.repositoryId%3A"
        )

        self.seen_product_links = set()

        test = [
            "https://www.gratis.com/ccstoreui/v1/search?N=695756508%202697991599&Nrpp=18&No=0&Nr=AND(product.active%3A1%2CNOT(sku.listPrice%3A0.000000))&Ns=",
            "https://www.gratis.com/loreal-paris-brow-artist-xpert-kas-maskarasi/urun/Lorealparis1001",
            "https://www.gratis.com/ccstoreui/v1/search?N=366766275+2235262767&Ns=&Nr=AND(product.active:1,NOT(sku.listPrice:0.000000))&No=18&Nf=&Nrpp=18",
        ]

        self.debug = kwargs.get("debug")
        if self.debug:
            self.start_urls = [
                "https://www.gratis.com/ccstoreui/v1/search?N=933953714%20679064841&Nrpp=18&No=0&Nr=AND(product.active%3A1%2CNOT(sku.listPrice%3A0.000000))&Ns="
            ]
        else:
            self.start_urls = GratisHelper.get_category_urls(self.base_url)

    def parse(self, response):
        data = json.loads(response.text)

        results = data.get("resultsList")
        records = results.get("records")

        products = list()
        ids = list()

        sub_records = [record.get("records") for record in records]
        sub_records = [s.pop() for s in sub_records if s]

        for sub_record in sub_records:
            info = sub_record.get("attributes")
            product = dict()

            routes = info.get("product.route")
            if not routes:
                continue
            link = self.base_url + routes.pop()
            barcodes = info.get("sku.gr_EanUpc")
            barcodes = BarcodeCleaner.get_clean_barcodes(barcodes)

            if len(barcodes) > 1:
                search_term = link.split("/")[-1]
                search_url = self.search_url + search_term
                if search_url not in self.seen_product_links:
                    self.seen_product_links.add(search_url)
                    yield scrapy.Request(url=search_url)

            repositoryId = info.get("sku.repositoryId").pop()
            ids.append(repositoryId)

            variant_key = info.get("sku.styleProperty")
            if variant_key:
                variant_key = "sku." + variant_key.pop()
                variant_name = info.get(variant_key)
                if variant_name:
                    product[keys.VARIANT_NAME] = variant_name.pop()
                    link += "?sku=" + repositoryId

            product[keys.LINK] = link
            product["repositoryId"] = repositoryId

            product[keys.BARCODES] = barcodes

            product[keys.NAME] = info.get("product.displayName").pop()

            product[keys.BRAND] = info.get("product.brand").pop()

            product[keys.SRC] = (
                self.base_url + info.get("product.primaryMediumImageURL").pop()
            )

            product[keys.MARKET] = keys.GRATIS

            if info.get("sku.availabilityStatus").pop() == "OUTOFSTOCK":
                product[keys.OUT_OF_STOCK] = True
            else:
                product[keys.OUT_OF_STOCK] = False

            products.append(product)

        discount_prices = GratisHelper.get_gratis_discounted_prices(ids)

        if discount_prices:
            for product in products:
                product[keys.PRICE] = discount_prices.get(product.get("repositoryId"))
                yield product


if __name__ == "__main__":
    debug_spider(GratisSpider)
    # GratisHelper.get_category_urls("https://www.gratis.com")
