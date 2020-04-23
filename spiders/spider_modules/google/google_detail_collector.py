import requests
import scrapy

import constants as keys
from spiders.spider_modules.base import BaseSpider
from spiders.spider_modules.google.google_detail_helper import GoogleHelper
from spiders.spider_modules.google.google_settings import GOOGLE_SETTINGS
from spiders.test_spider import debug_spider


class GoogleDetailSpider(BaseSpider):
    name = "google_detail"
    custom_settings = GOOGLE_SETTINGS

    def __init__(self, *args, **kwargs):
        super(GoogleDetailSpider, self).__init__(*args, base_domain="google.com")
        self.debug = kwargs.get("debug")

    def start_requests(self):

        """
                "https://www.google.com/shopping/product/7198253676429785863",
                "https://www.google.com/shopping/product/10002782510231755106",

        """
        if self.debug:
            gen = {"https://www.google.com/shopping/product/10026476884974776658"}
        else:
            gen = GoogleHelper.google_link_generator()

        for detail_url in gen:
            req = scrapy.Request(
                detail_url,
                callback=self.parse,
                meta={keys.LINK: detail_url},
                headers={
                    "Accept-Language": "tr, en",
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                },
            )
            yield req

    def parse(self, response):
        title = response.css("h1#product-name::text").extract_first()
        page_link = response.meta.get(keys.LINK)

        google_detail = {
            keys.NAME: title,
            keys.MARKET: keys.GOOGLE,
            keys.LINK: page_link,
        }

        id_lines = response.css("td.KhYrkb")
        id_info = [line.css("::text").extract_first() for line in id_lines]
        if id_info:
            google_detail[keys.GOOGLE_INFO] = id_info

        promoters = response.css("#os-sellers-table tr.os-row")
        promoted = self.parse_promoted(promoters)
        if promoted:
            google_detail[keys.PROMOTED] = promoted

        variants = self.parse_variants(response, page_link)
        if variants:
            google_detail[keys.VARIANTS] = variants

        yield google_detail

    @staticmethod
    def parse_promoted(promoters):
        promoted = dict()
        for row in promoters:
            link = row.css("span.os-seller-name-primary a::attr(href)").extract_first()

            name = row.css("span.os-seller-name-primary a::text").extract_first()
            name = "".join(name.lower().split())

            if not any(s in name for s in keys.ALLOWED_MARKET_LINKS):
                continue

            if "." in name:
                name = name.split(".")[0]

            if name not in keys.ALLOWED_MARKET_LINKS:
                continue

            r = requests.head(link, allow_redirects=True)
            clean_url = r.url
            if clean_url:
                promoted[name] = clean_url

        return promoted

    @staticmethod
    def parse_variants(response, page_link):
        variants_div = response.css("#variants")
        option_divs = variants_div.css("option")
        variants = dict()
        for option in option_divs:
            is_selected = option.css("::attr(selected)").extract_first()
            name = option.css("::text").extract_first()
            name = name.split("-")[0].strip()
            # mongo doesn't accept keys with . or $
            name = name.replace(".", ",").replace("$", "")
            if is_selected:
                link = "/shopping" + page_link.split("shopping")[1]
                variants[link] = name
                continue
            else:
                link = option.css("::attr(value)").extract_first()
                variants[link] = name
        return variants


if __name__ == "__main__":
    debug_spider(GoogleDetailSpider)
