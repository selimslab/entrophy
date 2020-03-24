import bs4
import requests

import constants as keys
from services.convertor import convert_price


class CarrefourHelper:
    @staticmethod
    def get_category_urls(c4_url):
        r = requests.get(c4_url)
        soup = bs4.BeautifulSoup(r.content, features="lxml")
        links = soup.find("ul", {"id": "category-1"}).findAll("li", recursive=False)
        urls = list()
        for link in links:
            a = link.find("a", href=True)
            href = a.get("href")
            name = a.getText().strip()
            if href and name:
                url = c4_url + href
                urls.append(url)

        return urls

    @staticmethod
    def extract_product_info(product_div, base_url):
        if product_div.css(".outOfStock"):
            return {}

        name = product_div.css("span.item-name::text").extract_first().strip()

        price = product_div.css("span.item-price::text").extract_first()
        price = price.replace(".", "").replace(",", ".").replace("TL", "").strip()
        price = convert_price(price)
        if not price:
            return {}

        src = product_div.css("img::attr(data-src)").extract_first()
        href = product_div.css("a::attr(href)").extract_first().strip()

        return {
            keys.LINK: base_url + href,
            keys.NAME: name,
            keys.SRC: src,
            keys.PRICE: price,
            keys.MARKET: keys.CARREFOUR,
            keys.OUT_OF_STOCK: False,
        }


if __name__ == "__main__":
    print(CarrefourHelper.get_category_urls("https://www.carrefoursa.com"))
