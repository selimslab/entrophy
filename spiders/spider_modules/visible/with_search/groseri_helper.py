import constants as keys
import services.collections_util
from services.convert_price import convert_price
from services.get_soup import get_soup


class TopLocalHelper:
    @staticmethod
    def get_category_urls(url):
        soup = get_soup(url)
        uls = soup.findAll("ul", {"class": "nav-tabs"})
        lis = [ul.findAll("li", recursive=False) for ul in uls]
        lis = services.collections_util.flatten(lis)
        hrefs = [li.find("a", href=True).get("href").strip() for li in lis]
        cat_urls = [url + href for href in hrefs]
        return cat_urls

    @staticmethod
    def extract_product_info(product_div, base_url):
        name = product_div.css(".caption a::text").extract_first()
        name = " ".join(name.split())

        # handle price
        price = product_div.css(".fiyat::text").extract_first()
        if "." in price:
            price = price.split(".")[0]
        price = price.replace(",", ".").replace("TL", "").strip()
        price = convert_price(price)
        if not price:
            return

        src = product_div.css(".product a img::attr(src)").extract_first()

        href = product_div.css(".product a::attr(href)").extract_first()

        return {
            keys.LINK: base_url + href,
            keys.NAME: name,
            keys.SRC: base_url + src,
            keys.PRICE: price,
            keys.MARKET: keys.GROSERI,
        }
