import constants as keys
import data_services.mongo.collections as collections


def mark_out_of_stock(links_seen: set, market_name: str):
    links = collections.items_collection.distinct(keys.LINK, {keys.MARKET: market_name})
    print(len(links_seen), len(links))
    if len(links_seen) < (len(links) / 4):
        print("very few links seen, there is a problem, do not mark")
        return

    removed_links = set(links) - links_seen

    collections.items_collection.update_many(
        {keys.MARKET: market_name, keys.LINK: {"$in": list(removed_links)}},
        {"$set": {keys.OUT_OF_STOCK: True}},
    )

    print(len(removed_links), "marked out_of_stock")
