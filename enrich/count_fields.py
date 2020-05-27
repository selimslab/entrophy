from pprint import pprint
from collections import Counter, OrderedDict

from data_services.mongo.collections import items_collection
import constants as keys
import services


def count_fields(docs, target_key):
    return sum(1 if target_key in doc else 0 for doc in docs)


def stat(docs):
    """ how many is guessed ? """
    with_brand = count_fields(docs, "brand")
    with_cat = count_fields(docs, "cat")

    print(
        "total",
        len(docs),
        "\n",

        "with_brand",
        with_brand,
        "\n",

        "with_cat",
        with_cat,
        "\n",
    )


def get_name_freq(full_skus: dict) -> dict:
    """ freq of tokens in all names """
    names = [doc.get("clean_names") for doc in full_skus.values()]
    names = services.collections_util.flatten(names)
    name_freq = Counter([word for name in names if name for word in name.split()])
    name_freq = OrderedDict(name_freq.most_common())
    return name_freq


def markets_with_cat():
    markets_with_cat = items_collection.distinct(
        keys.MARKET, {keys.CATEGORIES: {"$exists": True}}
    )
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
