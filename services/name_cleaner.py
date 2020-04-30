import re
import unicodedata


def clean_name(name: str) -> str:
    if not name:
        return ""

    name = (
        unicodedata.normalize('NFKD', name).encode('ascii', 'ignore')
            .replace("ı", "i")
            .replace("&", " ")
            .replace(",", ".")
    )
    allowed_chars = re.compile('[^a-zA-Z0-9,.* ]')
    name = allowed_chars.sub('', name)
    remove_whitespace_pattern = re.compile(r"\s+")
    name = re.sub(remove_whitespace_pattern, " ", str(name)).strip()
    # name = " ".join(name.strip().split())
    return name


def clean_for_sizing(s: str) -> str:
    if not s:
        return ""

    s = s.lower().replace("'", " ").replace(",", ".")
    remove_whitespace_pattern = re.compile(r"\s+")
    s = re.sub(remove_whitespace_pattern, " ", s)

    return s + " "
