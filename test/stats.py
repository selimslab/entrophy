from pprint import pprint

import constants as keys
import data_services.mongo.collections as collections


class Stats:
    @staticmethod
    def show_single_bar(name):
        bars = collections.items_collection.distinct(keys.BARCODES, {keys.MARKET: name})
        pprint(bars)
        print(len(set(bars)))

    @staticmethod
    def show_single_market_stats(name):
        this_market = {keys.MARKET: name}
        outofstock = {keys.OUT_OF_STOCK: True}
        bars = collections.items_collection.distinct(keys.BARCODES, {keys.MARKET: name})
        prom = collections.items_collection.distinct(keys.PROMOTED, {keys.MARKET: name})
        variants = collections.items_collection.distinct(
            keys.VARIANTS, {keys.MARKET: name}
        )
        variant_name = collections.items_collection.distinct(
            keys.VARIANT_NAME, {keys.MARKET: name}
        )

        count = collections.items_collection.count_documents(this_market)
        outofstock_count = collections.items_collection.count_documents(
            {**this_market, **outofstock}
        )

        report = [name, count, "docs"]
        if outofstock_count:
            report.append([outofstock_count, "out"])
        if bars:
            report.append([len(set(bars)), "barcode"])
        if prom:
            report.append([len(prom), "promoted"])
        if variants:
            report.append([len(variants), "variants"])
        if variant_name:
            report.append([len(variant_name), "variant_name"])

        pprint(report)

    @staticmethod
    def show_all_market_stats():
        print("total", collections.items_collection.count_documents({}))
        for name in keys.ALL_MARKETS:
            Stats.show_single_market_stats(name)

    @staticmethod
    def barcode_stats():
        bars = collections.items_collection.distinct(keys.BARCODES)
        print("all barcodes", len(set(bars)))

        sp = collections.items_collection.distinct(
            keys.BARCODES, {keys.MARKET: {"$in": keys.TRADITIONAL_MARKETS}}
        )
        print("supermarket_barcodes", len(sp))

        csm = collections.items_collection.distinct(
            keys.BARCODES, {keys.MARKET: {"$in": keys.COSMETICS_MARKETS}}
        )
        print("cosmetic_barcodes", len(csm))

        bby = collections.items_collection.distinct(
            keys.BARCODES, {keys.MARKET: {"$in": keys.BABY_MARKETS}}
        )
        print("baby_barcodes", len(bby))

        print("sp and csm", len(set(sp).union(set(csm))))
        print("baby and sp", len(set(sp).union(set(bby))))
        print("baby and csm", len(set(bby).union(set(csm))))


if __name__ == "__main__":
    # Stats.show_single_market_stats(keys.ALTUNBILEK)
    Stats.show_all_market_stats()

