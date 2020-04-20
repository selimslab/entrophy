import constants as keys
import data_services.mongo.collections as collections
import logging

def get_google_variants():
    logging.info("reading google variants..")
    return collections.items_collection.distinct(
        keys.VARIANTS, {keys.MARKET: keys.GOOGLE}
    )
