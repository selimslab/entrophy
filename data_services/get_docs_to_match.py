import constants as keys
import data_services.mongo.collections as collections


def get_docs_to_match(query: dict):
    projection = {
        "_id": 1,
        keys.LINK: 1,
        keys.NAME: 1,
        keys.SRC: 1,
        keys.MARKET: 1,
        keys.PRICE: 1,
        keys.OUT_OF_STOCK: 1,
        keys.BARCODES: 1,
        keys.PROMOTED: 1,
        keys.VARIANTS: 1,
        keys.VARIANT_NAME: 1,
        keys.SKU_ID: 1,
        keys.BRAND: 1,
        keys.COLOR: 1,
        keys.CATEGORIES: 1,

    }
    cursor = collections.items_collection.find(query, projection)
    return cursor
