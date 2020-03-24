import constants as keys
from services.convertor import convert_price
from services.get_soup import get_soup


class MopasHelper:
    @staticmethod
    def get_category_urls(url):
        soup = get_soup(url)
        ul = soup.find("ul", {"class": "nav-sidebar"})
        lis = ul.findAll("li", recursive=False)
        hrefs = [li.find("a", href=True).get("href").strip() for li in lis]
        cat_urls = [
            url + href for href in hrefs if "true" not in href and "yemek" not in href
        ]
        return cat_urls

    @staticmethod
    def extract_product_info(product_div, base_url):
        name = product_div.css(".product-title::text").extract_first()
        price = product_div.css(".sale-price::text").extract_first()
        price = price.replace(",", ".").replace("₺", "").strip()
        price = convert_price(price)
        if not price:
            return

        src = product_div.css(".image img::attr(src)").extract_first()
        href = product_div.css("a::attr(href)").extract_first()

        return {
            keys.LINK: base_url + href,
            keys.NAME: name,
            keys.SRC: src,
            keys.PRICE: price,
            keys.MARKET: keys.MOPAS,
        }
