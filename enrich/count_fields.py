from pprint import pprint
from collections import Counter, OrderedDict
from data_services.mongo.collections import items_collection
import constants as keys
import services
from paths import input_dir, output_dir


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


def inspect_brands():
    skus = services.read_json(input_dir / "full_skus.json").values()
    relevant_keys = {keys.BRANDS_MULTIPLE}
    skus = [services.filter_keys(doc, relevant_keys) for doc in skus]
    services.save_json(
        output_dir / "inspect_brands.json", skus,
    )


if __name__ == "__main__":
    pass
