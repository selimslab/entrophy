import requests
from bs4 import BeautifulSoup
from services.convertor import convert_price

import constants as keys


class N11Helper:
    @staticmethod
    def extract_product_info(response) -> dict:
        html_body = BeautifulSoup(str(response.text), "html.parser")
        parsed_detail = html_body.findAll("div", class_="pro")
        parsed_price = html_body.findAll("ins")
        p = dict()
        for product_div, price in zip(parsed_detail, parsed_price):
            product = product_div.find('a')
            product_name = product['title']
            url = product['href']
            src = product_div.find("img")['data-original']
            price = price.text \
                .replace(".", "") \
                .replace(",", ".") \
                .replace("TL", "") \
                .strip()
            p = {
                keys.LINK: url,
                keys.NAME: product_name,
                keys.SRC: src,
                keys.PRICE: convert_price(price),
                keys.MARKET: keys.N11,
            }

        return p

    @staticmethod
    def get_kozmetik_kisisel_bakim_urls(base_domain):
        categories_url = list()
        response = requests.get(base_domain)
        html_body = BeautifulSoup(response.text, "html.parser")
        parsed_html = html_body.findAll("li", class_="catMenuItem")
        category = ''
        for category_div in parsed_html:
            category = category_div.find('a')
            if "kozmetik" in category.text.lower():
                category = category_div
                break
        for subcategory in category.findAll("li", class_="subCatMenuItem"):
            categories_url.append('/' + ((subcategory.find('a')['href']).split('/'))[-1])

        return categories_url
