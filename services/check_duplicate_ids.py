import collections


def check_duplicate_ids(ids):
    dups = (item for item, count in collections.Counter(ids).items() if count > 1)
    return dups
