import constants as keys
import data_services.mongo.collections as collections
from spec.exceptions import LowItemCount
import logging


def mark_out_of_stock(links_seen: set, market_name: str):
    links = collections.items_collection.distinct(keys.LINK, {keys.MARKET: market_name})
    if len(links_seen) < (len(links) / 4):
        message = f"seen {len(links_seen)} of {len(links)} items in {market_name}"
        raise LowItemCount(message)

    removed_links = set(links) - links_seen

    collections.items_collection.update_many(
        {keys.MARKET: market_name, keys.LINK: {"$in": list(removed_links)}},
        {"$set": {keys.OUT_OF_STOCK: True}},
    )

    logging.info(f"{len(removed_links)} marked out_of_stock")
