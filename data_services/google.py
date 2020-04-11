import constants as keys
import data_services.mongo.collections as collections


def get_google_variants():
    return collections.items_collection.distinct(
        keys.VARIANTS, {keys.MARKET: keys.GOOGLE}
    )
