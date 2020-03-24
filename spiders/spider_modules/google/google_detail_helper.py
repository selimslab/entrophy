import constants as keys
import data_services.mongo.collections as collections


class GoogleHelper:
    @staticmethod
    def variant_link_generator():
        existing_google_links = collections.items_collection.distinct(
            keys.LINK, {keys.MARKET: keys.GOOGLE}
        )
        existing_google_links = set(existing_google_links)
        variants = collections.items_collection.distinct(
            keys.VARIANTS, {keys.MARKET: keys.GOOGLE}
        )
        for var in variants:
            variant_links = list(var.values())
            variant_links = ["https://www.google.com" + link for link in variant_links]
            variant_links = [
                link for link in variant_links if link not in existing_google_links
            ]
            for link in variant_links:
                yield link

    @staticmethod
    def google_link_generator():
        query = {keys.MARKET: keys.GOOGLE}
        links = collections.items_collection.distinct(keys.LINK, query)
        print(len(links), "distinct google links")

        for link in links:
            yield link
        for link in GoogleHelper.variant_link_generator():
            yield link
