import re
import unicodedata
from typing import List
import services


def remove_whitespace(s: str):
    remove_whitespace_pattern = re.compile(r"\s+")
    return re.sub(remove_whitespace_pattern, " ", str(s)).strip()


def test_remove_whitespace():
    assert remove_whitespace("a  b   c") == "a b c"


def normalize(s:str):
    return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")


def dot_iff_size(s):
    # only size can have .
    tokens = []
    for t in s.split():
        if not t.replace(".", "").isdigit():
            tokens.append(t.replace(".", " "))
        else:
            tokens.append(t)

    return " ".join(tokens)

def replace_chars(s:str):
    return (
        s.lower()
            .replace("ı", "i")
            .replace("&", " ")
            .replace("-", " ")
            .replace("/", " ")
            .replace(",", ".")
            .replace("*", " * ")
    )


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
    allowed_chars = re.compile("[^a-zA-Z0-9,.* ]")
    name = allowed_chars.sub("", name)
    name = remove_whitespace(name)
    return name


def test_clean_string():
    assert clean_string("Ülker   şğ  çİ") == "ulker sg ci"


if __name__ == "__main__":
    ...
