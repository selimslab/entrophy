from collections import OrderedDict, Counter
from operator import itemgetter
import itertools
from tqdm import tqdm
import re
from pprint import pprint

from paths import input_dir, output_dir
import services
import constants as keys


def get_sliding_window_freq():
    # known = get_known_strings()
    # known_pattern = re.compile("|".join(sorted(list(known), key=len, reverse=True)))
    brand_subcats_pairs_path = output_dir / "brand_subcats_pairs.json"
    brand_subcats_pairs = services.read_json(brand_subcats_pairs_path)

    known_brands = set(brand_subcats_pairs.keys())

    skus = services.read_json(input_dir / "full_skus.json").values()
    names = [sku.get(keys.CLEAN_NAMES, []) for sku in skus]
    names = services.flatten(names)
    names = [n for n in names if n]
    # names = [known_pattern.sub("", name) for name in tqdm(names[:100])]

    token_lists = services.get_token_lists(names)
    groups = []
    for token_list in tqdm(token_lists):
        for start in range(len(token_list)):
            for end in range(start + 1, len(token_list) + 1):
                # if first token is a brand
                if token_list[start] in known_brands:
                    s = " ".join(token_list[start:end]).strip()
                    groups.append(s)

    sliding_window_freq = OrderedDict(Counter(groups).most_common())
    sliding_window_freq = {
        s: freq for s, freq in sliding_window_freq.items() if freq > 10
    }

    to_remove = set()
    # remove if in another group
    for s, freq in sliding_window_freq.items():
        tokens = s.split()
        if len(tokens) < 3:
            continue

    pprint(to_remove)

    sorted_sliding = sorted(
        sliding_window_freq.items(),  # key=itemgetter(1), reverse=True
    )
    return OrderedDict(sorted_sliding)


if __name__ == "__main__":
    sliding_window_freq = get_sliding_window_freq()
    services.save_json(output_dir / "sliding_window_freq.json", sliding_window_freq)
