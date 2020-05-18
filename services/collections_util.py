"""
useful functions for lists, dicts, tuples, ..
"""
from collections import Counter, defaultdict


######### Dict util

def tree():
    return defaultdict(tree)


def get_most_frequent_key(d: dict):
    if d:
        return max(d, key=d.get)


def remove_nulls_from_list_values_of_a_dict(d: dict) -> dict:
    for k, v in d.items():
        if isinstance(v, list):
            d[k] = remove_null_from_list(v)
    return d


def remove_null_dict_values(d) -> dict:
    return {k: v for k, v in d.items() if v is not None}


def filter_empty_or_null_dict_values(d):
    return {k: v for k, v in d.items() if v or v is False}


def allow_string_keys_only(d: dict) -> dict:
    return {k: v for k, v in d.items() if isinstance(k, str) and v is not None}


######### List util


def get_n_most_common_list_elements(l: list, n: int) -> list:
    return [pair[0] for pair in Counter(l).most_common(n)]


def remove_null_from_list(l: list) -> list:
    return [x for x in l if x is not None]


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
