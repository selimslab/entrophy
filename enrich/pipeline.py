from pprint import pprint

import services
import constants as keys

import enrich
from paths import *

from data_services.mongo.collections import items_collection


def add_cat_and_brand():
    """
    1. get raw brands from websites
    2. get raw categories from myo, c4, migros, ty, gratis, watsons, joker, civil
    3. create a big brand list and a big category list
    4. clean brands and cats
    5. create an inverted index for brands and cats
    token: [all brands which includes this token]
    eg.
    loreal paris -> loreal : [all brands which includes loreal],
    paris: [all brands which includes paris]
    6.
    """

    full_skus = services.read_json(full_skus_path)

    guess_docs = enrich.create_guess_docs(full_skus.values())

    services.save_json(guess_docs_path, guess_docs)

    brand_index = services.read_json(brand_index_path)
    cat_index = services.read_json(cat_index_path)

    enrich.select_brand(guess_docs, brand_index)
    enrich.select_cat(guess_docs, cat_index)

    docs_with_brand_and_cat = [
        services.filter_empty_or_null_dict_values(doc) for doc in guess_docs
    ]

    services.save_json(docs_with_brand_and_cat_path, docs_with_brand_and_cat)

    enrich.stat(docs_with_brand_and_cat)


if __name__ == "__main__":
    markets_with_cat = items_collection.distinct(keys.MARKET, {keys.CATEGORIES: {"$exists": True}})
    pprint(markets_with_cat)
