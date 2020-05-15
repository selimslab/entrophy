import services
from pprint import pprint
from collections import defaultdict, Counter
from tqdm import tqdm
import itertools


def brand_cat_freq():
    # but they are sets already, freq=1 ?
    clean_brands = services.read_json("clean_brands.json")
    clean_cats = services.read_json("clean_cats.json")

    brand_freq = Counter([t for brand in clean_brands for t in brand.split()])
    cat_freq = Counter([t for cat in clean_cats for t in cat.split()])

    services.save_json("brand_freq.json", brand_freq)
    services.save_json("cat_freq.json", cat_freq)


def all_name_freq():
    """ freq of tokens in all names """
    groups = services.read_json("groups.json")
    names = (
        sku.get("clean_names")
        for product_id, skus in tqdm(groups.items())
        for sku_id, sku in skus.items()
    )
    names = services.flatten(list(names))

    name_freq = Counter([word for name in names if name for word in name.split()])
    services.save_json("name_freq.json", name_freq)


def stat():
    """ how many is guessed ? """
    groups = services.read_json("guess.json")
    with_brand_guess = sum(
        1 if "top_brand_guess" in sku else 0
        for product_id, skus in tqdm(groups.items())
        for sku_id, sku in skus.items()
    )

    with_cat_guess = sum(
        1 if "top_cat_guess" in sku else 0
        for product_id, skus in tqdm(groups.items())
        for sku_id, sku in skus.items()
    )

    print(with_cat_guess, with_brand_guess)


if __name__ == "__main__":
    stat()
