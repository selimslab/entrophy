import services
from collections import defaultdict
from typing import List


def tokenize(s: str):
    if s and isinstance(s, str):
        return [t.strip() for t in s.split()]


def tokenize_a_nested_list(nested_list: List[list]) -> list:
    flat_list = services.flatten(nested_list)
    strings = [s for s in flat_list if isinstance(s, str)]
    tokens_list = [tokenize(s) for s in strings]
    tokens = services.flatten(tokens_list)
    tokens = [t for t in tokens if t]
    return tokens


def create_inverted_index(strings: set, stopwords: set) -> dict:
    index = defaultdict(set)
    for str in strings:
        for token in str.split():
            if token in stopwords or len(token) == 1:
                continue
            index[token].add(str)
    index = {k: list(v) for k, v in index.items()}
    return index


def get_token_lists(names: list) -> List[list]:
    names = services.flatten(names)
    names = [n for n in names if n]
    name_tokens = [name.split() for name in names]
    return name_tokens


def test_tokenize_a_nested_list():
    x = tokenize_a_nested_list(["quick fox", "lazy dog"])
    assert set(x) == {"quick", "fox", "lazy", "dog"}
    y = tokenize_a_nested_list([{"quick fox"}, "lazy dog"])
    assert set(y) == {"lazy", "dog"}


if __name__ == "__main__":
    pass
