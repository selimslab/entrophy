import services
from pprint import pprint
from collections import defaultdict, Counter
from tqdm import tqdm
import itertools

import services.collections_util


def brand_cat_freq():
    # but they are sets already, freq=1 ?
    clean_brands = services.read_json("cleaner/clean_brands.json")
    clean_cats = services.read_json("cleaner/clean_cats.json")

    brand_freq = Counter([t for brand in clean_brands for t in brand.split()])
    cat_freq = Counter([t for cat in clean_cats for t in cat.split()])

    services.save_json("freq/brand_freq.json", brand_freq)
    services.save_json("freq/cat_freq.json", cat_freq)


def all_name_freq():
    """ freq of tokens in all names """
    groups = services.read_json("groups.json")
    names = (
        sku.get("clean_names")
        for product_id, skus in tqdm(groups.items())
        for sku_id, sku in skus.items()
    )
    names = services.collections_util.flatten(list(names))

    name_freq = Counter([word for name in names if name for word in name.split()])
    services.save_json("freq/name_freq.json", name_freq)



if __name__ == "__main__":
    stat()
