import constants as keys
from spec.model.spider_config import SpiderConfig
from services.string.convert_price import convert_price
from services.get_soup import get_soup
from spiders.spider_modules.base import BaseSpider
from spiders.test_spider import debug_spider


class TopLocalHelper:
    @staticmethod
    def get_category_urls(url):
        soup = get_soup(url)
        lis = soup.findAll("li", {"class": "single-level"})
        hrefs = [li.find("a", href=True).get("href").strip() for li in lis]
        hrefs = [h for h in hrefs if "indirim" not in h and "kampanya" not in h]
        cat_urls = [url + href for href in hrefs]
        return cat_urls

    @staticmethod
    def extract_product_info(product_div, base_url):
        name = product_div.css(".ems-prd-name a::text").extract_first().strip()

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

        src = product_div.css(
            ".ems-prd-image a img::attr(data-original)"
        ).extract_first()
        href = product_div.css(".ems-prd-image a::attr(href)").extract_first()

        return {
            keys.LINK: base_url + href,
            keys.NAME: name,
            keys.SRC: src,
            keys.PRICE: price,
            keys.MARKET: keys.COSMETICA,
        }


class CosmeticaSpider(BaseSpider):
    name = keys.COSMETICA

    def __init__(self, *args, **kwargs):
        config = SpiderConfig(
            is_basic=True,
            name=self.name,
            base_domain="cosmetica.com.tr",
            category_function=TopLocalHelper.get_category_urls,
            extract_function=TopLocalHelper.extract_product_info,
            table_selector=".urnList",
            product_selector=".ems-prd",
            next_page_href="a#ctl00_u34_ascUrunList_ascPagingDataAlt_lnkNext::attr(href)",
        )
        super().__init__(*args, **kwargs, config=config)


if __name__ == "__main__":
    debug_spider(CosmeticaSpider)
    # print(TopLocalHelper.get_category_urls("https://www.cosmetica.com.tr"))
