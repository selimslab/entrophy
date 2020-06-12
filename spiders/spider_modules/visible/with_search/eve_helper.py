import bs4
import requests

import constants as keys
from services.convert_price import convert_price


class EveHelper:
    @staticmethod
    def get_category_urls(url):
        r = requests.get(url)
        soup = bs4.BeautifulSoup(r.content, features="lxml")
        links = soup.findAll("li", {"class": "childs"})
        cat_urls = set()
        for link in links[:-1]:
            a = link.find("a", href=True)
            href = a.get("href")
            l = url + href
            l = l.split("/")[:4]
            l = "/".join(l)
            l += "/"
            cat_urls.add(l)

        return cat_urls

    @staticmethod
    def extract_product_info(product_div, base_url):

        brand = product_div.css(".prd-brand font::text").extract_first()
        if brand:
            brand = brand.strip()

        name = product_div.css(".prd-name a::text").extract_first()
        name_parts = [brand, name]
        name_parts = [n.strip() for n in name_parts if n]
        name = " ".join(name_parts)

        price = product_div.css(".urunListe_satisFiyat::text").extract()
        change = product_div.css(".urunListe_satisFiyat span.d::text").extract()

        price = " ".join(price + change)
        price = (
            price.replace("TL", "")
            .replace(".", "")
            .replace(",", ".")
            .replace(" ", "")
            .strip()
        )
        price = convert_price(price)
        if not price:
            return

        href = product_div.css(".prd-name a::attr(href)").extract_first()

        src = (
            product_div.css(".prd-image img::attr(data-original)")
            .extract_first()
            .strip()
        )

        return {
            keys.LINK: base_url + href,
            keys.NAME: name,
            keys.SRC: base_url + src,
            keys.PRICE: price,
            keys.MARKET: keys.EVESHOP,
            keys.OUT_OF_STOCK: False,
        }
