import bs4
import requests

import constants as keys
from services import convert_price


class MigrosHelper:
    @staticmethod
    def get_urls_migros(migros_url):
        r = requests.get(migros_url)
        soup = bs4.BeautifulSoup(r.content, features="lxml")
        links = soup.findAll("li", {"class": "category-list-item"})
        links = links[: len(links) // 2]

        urls = list()
        for link in links:
            a = link.find("a", href=True)
            # category = a.getText().strip()
            href = a.get("href").strip()
            url = migros_url + href
            urls.append(url)
        return urls

    @staticmethod
    def extract_product_info(product_div, base_url):

        name = product_div.css("h5.product-card-title a::text").extract_first().strip()

        price = product_div.css("div.price-tag span.value::text").extract_first()
        if "." in price:
            price = price.split(".")[0]

        price = price.replace(",", ".").replace("TL", "").strip()
        price = convert_price(price)
        if not price:
            return

        href = product_div.css(".product-link::attr(href)").extract_first().strip()
        src = product_div.css("img::attr(data-src)").extract_first()

        return {
            keys.LINK: base_url + href,
            keys.NAME: name,
            keys.SRC: src,
            keys.PRICE: price,
            keys.MARKET: keys.MIGROS,
            keys.OUT_OF_STOCK: False,
        }


if __name__ == "__main__":
    MigrosHelper.get_urls_migros("https://www.migros.com.tr")
