from bs4 import BeautifulSoup

import constants as keys
from services.convertor import convert_price


class GittigidiyorHelper:
    @staticmethod
    def extract_product_info(product) -> dict:
        product_name = product['title']
        url = (product['href'])[2:]
        src = product.find("img", class_="img-cont")['data-original']
        price_div = product.find("div", class_="gg-w-24 gg-d-24 gg-t-24 gg-m-24 padding-none product-price-info")
        price = (price_div.find("p")).text \
            .replace(".", "") \
            .replace(",", ".") \
            .replace("TL", "") \
            .strip()
        p = {
            keys.LINK: url,
            keys.NAME: product_name,
            keys.SRC: src,
            keys.PRICE: convert_price(price),
            keys.MARKET: keys.GITTIGIFIYOR,
        }

        return p
