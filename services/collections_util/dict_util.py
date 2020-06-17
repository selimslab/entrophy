from collections import Counter, defaultdict, ChainMap
from typing import Iterable, List, Callable


def tree():
    return defaultdict(tree)


def merge_list_of_dicts(ld: List[dict]) -> dict:
    return dict(ChainMap(*ld))


def get_most_frequent_key(d: dict):
    if d:
        return max(d, key=d.get)


def get_most_common_item(itr: Iterable):
    return Counter(itr).most_common(1)[0][0]


def test_get_most_common_item():
    assert get_most_common_item([(2, 3), (2, 3), 4, 5, "a"]) == (2, 3)


def filter_dict(d: dict, filter_func: Callable):
    return {k: v for k, v in d.items() if filter_func(k, v)}


def remove_nulls_from_list_values_of_a_dict(d: dict) -> dict:
    for k, v in d.items():
        if isinstance(v, list):
            d[k] = remove_none_from_list(v)
    return d


def remove_null_dict_values(d) -> dict:
    return {k: v for k, v in d.items() if v is not None}


def filter_empty_or_null_dict_values(d):
    return {k: v for k, v in d.items() if v or v is False}


def filter_keys(d: dict, allowed_keys: set) -> dict:
    return {k: v for k, v in d.items() if k in allowed_keys}


def allow_string_keys_only(d: dict) -> dict:
    return {k: v for k, v in d.items() if isinstance(k, str) and v is not None}


def merge_nested_dict(d: dict):
    """
    d = {
        a: {
            colors: ["white"]
        },

        b: {
            colors: ["blue"]
        },
    }

    merged = {
    colors : ["white", "blue"]
    }
    """
    merged = defaultdict(set)  # uses set to avoid duplicates

    for key, nested_dict in d.items():
        for k, v in nested_dict.items():  # use d.iteritems() in python 2
            merged[k].update(v)

    return merged


def convert_dict_set_values_to_list(d: dict) -> dict:
    return {k: list(v) for k, v in d.items()}


def count_fields(docs: List[dict], target_key: str):
    return sum(1 if target_key in doc else 0 for doc in docs)
