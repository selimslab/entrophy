import re


def tr_lower(to_lower: str) -> str:
    spec = {"İ": "i", "I": "ı", "Ç": "ç", "Ğ": "ğ", "Ö": "ö", "Ş": "ş"}
    for ch in spec:
        if ch in to_lower:
            to_lower.replace(ch, spec[ch])
    return to_lower.lower()


def clean_name(name: str) -> str:
    if not name:
        return ""

    name = (
        tr_lower(name)
            .replace("&", " ")
            .replace("'", "")
            .replace("-", "")
            .replace(",", ".")
            .replace("é", "e")
            .replace("ç", "c")
            .replace("ş", "s")
            .replace("ğ", "g")
            .replace("ı", "i")
            .replace("ö", "o")
            .replace("ü", "u")
    )
    remove_whitespace_pattern = re.compile(r"\s+")
    name = re.sub(remove_whitespace_pattern, " ", name).strip()
    # name = " ".join(name.strip().split())
    return name


def clean_for_sizing(s: str) -> str:
    if not s:
        return ""

    s = s.lower().replace("'", " ").replace(",", ".")
    remove_whitespace_pattern = re.compile(r"\s+")
    s = re.sub(remove_whitespace_pattern, " ", s)

    return s + " "
