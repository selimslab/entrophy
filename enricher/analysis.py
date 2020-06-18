import logging
from typing import List
from collections import defaultdict, Counter, OrderedDict

import services
import constants as keys
import paths as paths



def sort_subcat():
    # sort by most common
    subcat_freq = services.read_json("out/subcat_freq.json")
    services.save_json("out/subcat_freq.json", OrderedDict(Counter(subcat_freq).most_common()))

def analyze_subcat():
    # which subcats are assigned ?
    products_out = services.read_json(paths.products_out)
    subcats_assigned = [p.get(keys.SUBCAT) for p in products_out]
    subcats_assigned = services.flatten(subcats_assigned)
    # subcats_assigned = list(set(subcats_assigned))

    # by which freq
    services.save_json("out/subcats_assigned.json", OrderedDict(Counter(subcats_assigned).most_common()))



def analyze_brand():
    products_out = services.read_json(paths.products_out)
    subcats_assigned = [p.get(keys.SUBCAT) for p in products_out]
    subcats_assigned = services.flatten(subcats_assigned)
    # subcats_assigned = list(set(subcats_assigned))

    # by which freq
    services.save_json("out/subcats_assigned.json", OrderedDict(Counter(subcats_assigned).most_common()))

    with_brand_only = services.read_json(paths.output_dir / "with_brand_only.json")


if __name__ == "__main__":
    ...

