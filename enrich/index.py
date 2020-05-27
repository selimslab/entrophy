from collections import defaultdict, Counter, OrderedDict
from typing import List

import services
from paths import *


def create_inverted_index(words: set):
    stopwords = {"ml", "gr", "adet", "ve", "and", "ile"}
    index = defaultdict(set)
    for word in words:
        for token in word.split():
            if token in stopwords or len(token) == 1:
                continue
            index[token].add(word)
    index = {k: list(v) for k, v in index.items()}
    return index


def create_index(words: List[str], name: str) -> dict:
    words = services.clean_list_of_strings(words)
    words = services.remove_null_from_list(words)
    # but they are sets already, freq=1 ?
    word_freq = Counter([t for brand in words for t in brand.split()])
    word_freq = OrderedDict(word_freq.most_common())
    index = create_inverted_index(set(words))

    freq_file = name + "_freq.json"
    clean_file = name + "_clean.json"
    index_file = name + "_index.json"

    services.save_json(output_dir / freq_file, word_freq)
    services.save_json(output_dir / clean_file, words)
    services.save_json(output_dir / index_file, index)

    return index


def get_brand_index():
    brands = services.read_json(
        input_dir / "joined_brands.json").get("brands")
    brand_index = create_index(brands, "brands")
    return brand_index


def get_cat_index():
    cats = services.read_json(
        input_dir / "joined_categories.json").get("categories")
    cat_index = create_index(cats, "cats")
    return cat_index


if __name__ == "__main__":
    ...
