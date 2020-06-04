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


def experiment_with_subbrands():
    path = output_dir / "most_frequent_start_strings.json"
    freq = services.read_json(path)

    brands_from_markets = services.read_json(output_dir / "brands_from_markets.json")

    sub_brands = {}

    for s, count in freq.items():

        tokens = s.split()
        if len(tokens) > 4:
            continue
        if len(tokens) == 1:
            sub_brands[s] = count
            continue

        prev = " ".join(tokens[:-1])
        prev_freq = freq.get(prev, float("infinity"))
        root_freq = freq.get(tokens[0], float("infinity"))
        if count > root_freq * 0.1 and prev_freq * 0.2 < count < prev_freq * 0.8:
            print(" ".join(tokens), count, prev, prev_freq)

            sub_brands[prev] = prev_freq

    # filter if already in brands_from_markets
    sub_brands = {k: v for k, v in sub_brands.items() if k not in set(brands_from_markets)}
    services.save_json(output_dir / "sub_brands.json", OrderedDict(sorted(sub_brands.items())))


def experiment_sliding_window_freq():
    from main import get_token_lists
    known = get_known_strings()
    known_pattern = re.compile("|".join(known))

    skus = services.read_json(input_dir / "full_skus.json").values()
    names = [sku.get(keys.CLEAN_NAMES, []) for sku in skus]
    names = services.flatten(names)
    names = [n for n in names if n]
    names = [known_pattern.sub("", name) for name in tqdm(names[:100])]

    token_lists = get_token_lists(names)
    groups = []
    for token_list in tqdm(token_lists):
        for start in range(len(token_list)):
            for end in range(start + 1, len(token_list) + 1):
                s = " ".join(token_list[start:end]).strip()
                groups.append(s)
    sliding_window_freq = OrderedDict(Counter(groups).most_common())
    sliding_window_freq = {
        s: freq for s, freq in sliding_window_freq.items() if freq > 1
    }

    sorted_sliding = sorted(sliding_window_freq.items(), key=itemgetter(1), reverse=True)
    services.save_json(output_dir / "brand_cat_removed.json",
                       OrderedDict(sorted_sliding)
                       )


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


if __name__ == "__main__":
    remove_known_from_slidings()
