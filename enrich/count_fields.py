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


def inspect_brand():
    skus_with_brand = services.read_json(output_dir / "skus_with_brand.json")
    brands = [sku.get("brand") for sku in skus_with_brand]
    brands = sorted(set(brands), key=len, reverse=True)

    brand_tree = services.read_json(output_dir / "brand_tree.json")
    in_brand_tree = set(brand_tree.keys())

    print("in_brand_tree", len(in_brand_tree))
    print("sku brands", len(brands))
    print("common", len(in_brand_tree.intersection(brands)))
    print("diff", len(set(brands).difference(in_brand_tree)))


if __name__ == "__main__":
    pass
