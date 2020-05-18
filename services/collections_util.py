"""
useful functions for lists, dicts, tuples, ..
"""


def get_most_frequent_key(d: dict):
    if d:
        return max(d, key=d.get)


def remove_null_from_list(l: list) -> list:
    return [x for x in l if x is not None]


def remove_nulls_from_list_values_of_a_dict(d: dict) -> dict:
    for k, v in d.items():
        if isinstance(v, list):
            d[k] = remove_null_from_list(v)
    return d


def remove_null_dict_values(d) -> dict:
    return {k: v for k, v in d.items() if v is not None}


def allow_string_keys_only(d: dict) -> dict:
    return {k: v for k, v in d.items() if isinstance(k, str) and v is not None}
