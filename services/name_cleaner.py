import re
import unicodedata
from typing import List
import services

def clean_name(name: str) -> str:
    if not name:
        return ""
    # replace accented chars with their base forms
    name = (
        name.lower()
            .replace("ı", "i")
            .replace("&", " ")
            .replace("-", " ")
            .replace("/", " ")
            .replace(",", ".")
            .replace("*", " * ")
    )
    name = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode("ascii")
    allowed_chars = re.compile("[^a-zA-Z0-9,.* ]")
    name = allowed_chars.sub("", name)

    remove_whitespace_pattern = re.compile(r"\s+")
    name = re.sub(remove_whitespace_pattern, " ", str(name)).strip()

    # only size can have .
    tokens = []
    for t in name.split():
        if not t.replace(".", "").isdigit():
            tokens.append(t.replace(".", " "))
        else:
            tokens.append(t)

    name = " ".join(tokens)

    return name


def clean_list_of_strings(l: List[str]):
    return [clean_name(x) for x in l]


def list_to_clean_set(strs: list):
    res = clean_list_of_strings(strs)
    res = services.remove_null_from_list(res)
    res = sorted(list(set(res)))
    return res


if __name__ == "__main__":
    x = clean_name("eti̇ peti̇to")
    print(x)
