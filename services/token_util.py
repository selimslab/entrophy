from collections import Counter

from services import flattener
from services import name_cleaner


def tokenize(s):
    tokens = name_cleaner.clean_name(s).split()
    return [t.strip() for t in tokens if len(t) > 2]


def get_tokens_of_a_group(strings: list):
    strings = [s for s in strings if isinstance(s, str)]
    tokens_list = [tokenize(s) for s in strings]
    tokens = flattener.flatten(tokens_list)
    return tokens


def get_n_most_common_tokens(tokens: list, n: int) -> list:
    return [pair[0] for pair in Counter(tokens).most_common(n)]


if __name__ == "__main__":
    pass
