import json

import requests

import constants as keys
from services.convertor import convert_price


class A101Helper:
    @staticmethod
    def get_category_urls():
        api_1 = "https://www.a101.com.tr/menus/generate/?format=json&depth_height=1"
        api_2 = "https://www.a101.com.tr/menus/generate/?format=json&depth_height=2"

        r = requests.get(api_1)
        data = json.loads(r.content)
        cats = data.get("menu")

        parent_cats = dict()
        for cat in cats:
            label = cat.get("label")
            url = cat.get("url")
            parent_cats[label] = url

        r = requests.get(api_2)
        data = json.loads(r.content)
        cats = data.get("menu")

        urls = list()
        unwanted_cats = {}  # {"oto-bahce", "kitap", "ev-yasam", "elektronik"}
        for cat in cats:
            label = cat.get("label")
            if label in parent_cats:
                continue

            url = cat.get("url")

            if any(uwc in url for uwc in unwanted_cats):
                continue
            urls.append(url)

        return urls

    @staticmethod
    def extract_product_info(product, base_url) -> dict:
        name = product.css(".name::text").extract_first().strip()

        price = product.css(".prices span.current::text").extract_first()

        price = price.replace(".", "").replace(",", ".").replace("TL", "").strip()
        price = convert_price(price)
        if not price:
            return {}

        src = product.css(".product-image img::attr(src)").extract_first()
        href = product.css("a::attr(href)").extract_first().strip()

        p = {
            keys.LINK: base_url + href,
            keys.NAME: name,
            keys.SRC: src,
            keys.PRICE: price,
            keys.MARKET: keys.A101,
            keys.OUT_OF_STOCK: False,
        }

        if product.css(".out-of-stock"):
            p[keys.OUT_OF_STOCK] = True

        badge_text = product.css(".badge::text").extract_first()
        if badge_text and badge_text.strip() == "SADECE ONLINE":
            p[keys.OUT_OF_STOCK] = True

        return p
