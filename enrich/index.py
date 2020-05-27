from collections import defaultdict, Counter
import services
from paths import *
from tqdm import tqdm

from typing import List


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


def create_index(words: List[str], name: str):
    words = services.clean_list_of_strings(words)
    words = services.remove_null_from_list(words)
    # but they are sets already, freq=1 ?
    word_freq = Counter([t for brand in words for t in brand.split()])
    index = create_inverted_index(set(words))

    services.save_json(temp / name + "_freq.json", word_freq)
    services.save_json(temp / "clean_" + name + ".json", words)
    services.save_json(temp / name + "_index", index)


def create_brand_and_cat_index():
    brands = services.read_json("cleaner/joined_brands.json").get("brands")
    cats = services.read_json("cleaner/joined_categories.json").get("categories")
    create_index(brands, "brand")
    create_index(cats, "category")


def all_name_freq():
    """ freq of tokens in all names """
    guess_docs = services.read_json(guess_docs_path)
    names = [doc.get("clean_names") for doc in guess_docs]
    names = services.collections_util.flatten(names)
    name_freq = Counter([word for name in names if name for word in name.split()])
    services.save_json("freq/name_freq.json", name_freq)


if __name__ == "__main__":
    ...
