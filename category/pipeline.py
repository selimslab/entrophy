from pprint import pprint

import services
import constants as keys

from paths import *

from data_services.mongo.collections import items_collection

from .prepare_docs_to_guess import create_guess_docs
from .guess import select_cat_and_brand
from .stat import stat


def add_cat_and_brand():
    full_skus_path = temp / "full_skus.json"

    full_skus = services.read_json(full_skus_path)

    guess_docs = create_guess_docs(full_skus.values())

    services.save_json(guess_docs_path, guess_docs)

    brand_index = services.read_json(brand_index_path)
    cat_index = services.read_json(cat_index_path)

    docs_with_brand_and_cat = select_cat_and_brand(guess_docs, brand_index, cat_index)

    services.save_json(docs_with_brand_and_cat_path, docs_with_brand_and_cat)

    stat(docs_with_brand_and_cat)


if __name__ == "__main__":
    markets_with_cat = items_collection.distinct(keys.MARKET, {keys.CATEGORIES: {"$exists": True}})
    pprint(markets_with_cat)
