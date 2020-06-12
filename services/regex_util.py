import re


def remove_non_alpha_numeric_chars(s: str) -> str:
    return re.sub("[^\w]", " ", s)


def remove_whitespace(s: str):
    remove_whitespace_pattern = re.compile(r"\s+")
    return re.sub(remove_whitespace_pattern, " ", str(s)).strip()


def test_remove_whitespace():
    assert remove_whitespace("a  b   c") == "a b c"
