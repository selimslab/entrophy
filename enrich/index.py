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


def create_index(words: List[str], name: str) -> dict:
    words = services.clean_list_of_strings(words)
    words = services.remove_null_from_list(words)
    # but they are sets already, freq=1 ?
    word_freq = Counter([t for brand in words for t in brand.split()])
    index = create_inverted_index(set(words))

    freq_file = name + "_freq.json"
    clean_file = name + "_clean.json"
    index_file = name + "_index.json"

    services.save_json(temp / freq_file, word_freq)
    services.save_json(temp / clean_file, words)
    services.save_json(temp / index_file, index)

    return index


if __name__ == "__main__":
    ...
