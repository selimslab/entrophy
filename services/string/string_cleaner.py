import re
import unicodedata
import logging

from typing import List, Iterable
import services


def remove_patterns_from_string(s: str, to_remove: Iterable) -> str:
    for bad in to_remove:
        s = s.replace(bad, "")
    s = services.remove_whitespace(s)
    return s


def normalize(s: str):
    return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")


def dots_to_separate_digits_only(s: str) -> str:
    # 1.2 ok
    # 3123 ml. fail
    tokens = []
    for t in s.split():
        if not t.replace(".", "").isdigit():
            tokens.append(t.replace(".", " "))
        else:
            tokens.append(t)

    return " ".join(tokens)


def test_dots_to_separate_digits_only():
    cases = [("1.2", "1.2"), ("34 ml.", "34 ml "), ("a 1.3.5 b", "a 1.3.5 b")]
    services.check(dots_to_separate_digits_only, cases)


def replace_chars(s: str):
    return (
        s.lower()
        .replace("ı", "i")
        .replace("&", " ")
        .replace("-", " ")
        .replace("/", " ")
        .replace(",", ".")
        .replace("*", " * ")
    )


def plural_to_singular(s: str):
    n = 4
    first_part, ending = s[:-n], s[-n:]
    plural = ["leri", "lari", "ler", "lar"]

    for p in plural:
        if p in ending:
            ending = ending.replace(p, "")

    return first_part + ending


def test_plural_to_singular():
    assert plural_to_singular("selimleri") == "selim"
    assert plural_to_singular("selimlar") == "selim"
    assert plural_to_singular("selimlari") == "selim"


def remove_stopwords(tokens: list) -> list:
    stopwords = {"ml", "gr", "kg", "adet", "ve", "and", "ile", "for", "icin"}
    return [t for t in tokens if t not in stopwords]


def is_single_letter(s: str) -> bool:
    return len(s) == 1 and not s.isdigit()


def is_barcode(s: str) -> bool:
    return s.isdigit() and len(s) in {8, 10, 11, 13}


def is_mixed_letters_and_words(s: str):
    """ nonsense like adas42342 """
    return len(s) > 5 and (s.isalnum() and not s.isdigit() and not s.isalpha())


def clean_string(name: str) -> str:
    """
    replace turkish chars
    allowed chars are a-z A-Z 0-9 and , . * are, remove all else
    remove whitespace
    only size can have a dot . char, other dots are removed
    """
    if not name:
        return ""
    # replace accented chars with their base forms
    name = replace_chars(name)
    name = normalize(name)
    allowed_chars = re.compile("[^a-zA-Z0-9,. ]")
    name = allowed_chars.sub("", name)
    name = dots_to_separate_digits_only(name)
    name = services.remove_whitespace(name)
    return name


def test_clean_string():
    assert clean_string("Ülker   şğ  çİ") == "ulker sg ci"


if __name__ == "__main__":
    ...
