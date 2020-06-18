from collections import Counter
from typing import Iterable


def get_most_common_item(itr: Iterable):
    return Counter(itr).most_common(1)[0][0]


def test_get_most_common_item():
    assert get_most_common_item([(2, 3), (2, 3), 4, 5, "a"]) == (2, 3)


def sort_from_long_to_short(it: Iterable) -> list:
    return sorted(list(it), key=len, reverse=True)


def get_n_most_common_list_elements(l: list, n: int) -> list:
    return [pair[0] for pair in Counter(l).most_common(n)]


def remove_none_from_list(l: list) -> list:
    return [x for x in l if x is not None]


def dedup_denull(l: list) -> list:
    return list(set(i for i in l if i))


def flatten(l: list) -> list:
    if not l:
        return []
    flat_list = []
    for i in l:
        if not isinstance(i, list):
            flat_list.append(i)
        else:
            flat_list += flatten(i)
    return flat_list
