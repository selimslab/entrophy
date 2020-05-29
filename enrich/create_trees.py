from collections import defaultdict
from pprint import pprint

import services
from paths import input_dir, output_dir
from data_services.mongo.collections import items_collection
import constants as keys


def brand_variants():
    """
        johnson s baby -> johnsons baby

    """
    brand_tree = services.read_json(input_dir / "brand_tree.json")
    brands = brand_tree.keys()
    suspects = []  # with single tokens

    pprint(list(sorted(brands)))


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


def inspect():
    brand_tree = services.read_json(output_dir / "brand_tree.json")
    # pprint(brand_tree.keys())

    brands_clean = services.read_json(output_dir / "brands_clean.json")

    brands_clean = [b for b in brands_clean if b]

    print(len(set(brands_clean).union(set(brand_tree.keys()))))

    diff = set(brands_clean).difference(set(brand_tree.keys()))
    pprint(diff)


if __name__ == "__main__":
    # create_trees()
    """
    idea: full_skus can help brand tree
    """
    inspect()
