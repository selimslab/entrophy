from collections import Counter, OrderedDict
from typing import Iterable


def sorted_counter(it: Iterable):
    """ get a sorted counter of an iterable """
    return OrderedDict(Counter(it).most_common())


def sort_from_long_to_short(it: Iterable) -> list:
    return sorted(list(it), key=len, reverse=True)


def get_most_common_item(itr: Iterable):
    return Counter(itr).most_common(1)[0][0]


def test_get_most_common_item():
    assert get_most_common_item([(2, 3), (2, 3), 4, 5, "a"]) == (2, 3)
