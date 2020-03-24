from pprint import pprint

import constants as keys
import data_services.mongo.collections as collections


class Cleaner:
    @staticmethod
    def check_promoted():
        prom = collections.items_collection.distinct(keys.PROMOTED)
        print(len(prom))
        count = 0
        for p in prom:
            count += len(p)
            for seller, link in p.items():
                if "?" in link:
                    print(link)

        print(count, "links in total")

    @staticmethod
    def check_prices():
        prices = collections.items_collection.distinct(keys.PRICE)
        pprint(prices)


if __name__ == "__main__":
    Cleaner.check_prices()
