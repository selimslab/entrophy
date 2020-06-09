from collections import OrderedDict, Counter
from operator import itemgetter
import itertools
from tqdm import tqdm
import re

from paths import input_dir, output_dir
import services
import constants as keys


def get_brands_from_markets():
    brand_subcats_pairs_path = output_dir / "brand_subcats_pairs.json"
    brand_subcats_pairs = services.read_json(brand_subcats_pairs_path)
    return sorted(list(brand_subcats_pairs.keys()), key=len, reverse=True)





def get_known_strings():
    brand_subcats_pairs_path = output_dir / "brand_subcats_pairs.json"
    brand_subcats_pairs = services.read_json(brand_subcats_pairs_path)

    known_brands = set(brand_subcats_pairs.keys())
    subcats = set(itertools.chain.from_iterable(brand_subcats_pairs.values()))

    known = known_brands.union(subcats)
    return known


def remove_size():
    ...


def remove_known_from_slidings():
    known = get_known_strings()
    known = [k for k in known if len(k) > 4]
    known_pattern = re.compile("|".join(known))

    skus = services.read_json(input_dir / "full_skus.json").values()
    names = [sku.get(keys.CLEAN_NAMES, []) for sku in skus]
    names = services.flatten(names)
    names = [n for n in names if n]
    brand_cat_removed = [known_pattern.sub("", name).strip() for name in tqdm(names)]

    services.save_json(output_dir / "brand_cat_removed.json", brand_cat_removed)


def sub_exp2():
    """
    if we give the correct brands, the data to look for type will be cleaner
    """
    path = output_dir / "most_frequent_start_strings.json"
    freq = services.read_json(path)

    # filter if already in brands_from_markets
    brands_in_results = services.read_json(output_dir / "brands_in_results.json")
    freq = {
        k: v
        for k, v in freq.items()
        if k not in set(brands_in_results) and 1 < len(k.split()) < 5
    }
    services.save_json(
        output_dir / "exp_sub_brand.json", OrderedDict(sorted(freq.items()))
    )


