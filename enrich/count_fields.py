from pprint import pprint
from data_services.mongo.collections import items_collection
import constants as keys


def count_fields(docs, target_key):
    return sum(1 if target_key in doc else 0 for doc in docs)


def stat(docs):
    """ how many is guessed ? """
    with_brand = count_fields(docs, "brand")
    with_cat = count_fields(docs, "cat")

    with_brand_guess = count_fields(docs, "top_brand_guess")
    with_cat_guess = count_fields(docs, "top_cat_guess")

    print(
        with_brand, with_brand_guess, with_cat, with_cat_guess,
    )


def markets_with_cat():
    markets_with_cat = items_collection.distinct(keys.MARKET, {keys.CATEGORIES: {"$exists": True}})
    pprint(markets_with_cat)
    """
['basgimpa',
 'begendik',
 'carrefoursa',
 'celikkayalar',
 'cergibozanlar',
 'egesok',
 'furpa',
 'gratis',
 'migros',
 'oli',
 'onur',
 'rammar',
 'show',
 'snowy',
 'ty',
 'yunus']
    """
