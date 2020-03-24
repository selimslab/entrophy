import bs4
import requests

import constants as keys
from services import convert_price


class WatsonsHelper:
    @staticmethod
    def get_category_urls(base_url):
        r = requests.get(base_url)
        soup = bs4.BeautifulSoup(r.content, features="lxml")
        urls = list()
        links = soup.findAll("a", {"class": "main-menu-link"})
        for link in links:
            href = link.get("href")
            url = base_url + href
            if "sayfa" not in url and url not in urls:
                urls.append(url)

        return urls

    @staticmethod
    def extract_product_info(product_div, base_url):

        brand = product_div.css(".productbox-name::text").extract_first().strip()
        # name = product_div.css(".productbox-desc::text").extract_first().strip()
        name = (
            product_div.css(".product-box-zoom-image::attr(title)")
            .extract_first()
            .strip()
        )
        name = " ".join([brand, name])

        price = product_div.css(".product-box-price::text").extract_first()

        price = price.replace("₺", "").replace(".", "").replace(",", ".").strip()

        price = convert_price(price)
        if not price:
            return

        href = product_div.css(
            ".product-box-image-container a::attr(href)"
        ).extract_first()

        src = (
            product_div.css(".product-box-zoom-image::attr(src)")
            .extract_first()
            .strip()
        )

        product = {
            keys.LINK: base_url + href,
            keys.NAME: name,
            keys.PRICE: price,
            keys.MARKET: keys.WATSONS,
            keys.BRAND: brand,
            keys.OUT_OF_STOCK: False,
        }

        if "default" not in src:
            product[keys.SRC] = src

        if product_div.css(".product-box-has-no-stock"):
            product[keys.OUT_OF_STOCK] = True

        return product
