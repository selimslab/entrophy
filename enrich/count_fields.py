from pprint import pprint
from collections import Counter, OrderedDict

from data_services.mongo.collections import items_collection
import constants as keys
import services

from paths import input_dir


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


def markets_with_cat():
    markets_with_cat = items_collection.distinct(
        keys.MARKET, {keys.CATEGORIES: {"$exists": True}}
    )
    pprint(markets_with_cat)  # myo, wat, gratis, c4, ross, ty, migros

    markets_with_brand = items_collection.distinct(
        keys.MARKET, {keys.BRAND: {"$exists": True}}
    )
    pprint(markets_with_brand)  # myo, wat, gratis, c4, ross, ty


def cat_brand_pairs():
    q = {keys.CATEGORIES: {"$exists": True}, keys.BRAND: {"$exists": True}}
    proj = {keys.CATEGORIES: 1, keys.BRAND: 1, "_id": 0}
    cursor = items_collection.find(q, proj)
    services.save_json(input_dir / "brand_cat_pairs.json", list(cursor))


def first_word_freq():
    full_skus = services.read_json(input_dir / "full_skus.json")
    names = [doc.get("clean_names", []) for doc in full_skus.values()]
    names = services.flatten(names)
    names = [n for n in names if n]
    first_tokens = [name.split()[0] for name in names]
    first_tokens = [n for n in first_tokens if len(n) > 2]

    first_token_freq = services.get_ordered_token_freq_of_a_nested_list(first_tokens)
    first_token_freq = {token: freq for token, freq in first_token_freq.items() if freq > 100}
    services.save_json(input_dir / "first_token_freq.json", first_token_freq)


if __name__ == "__main__":
    first_word_freq()
