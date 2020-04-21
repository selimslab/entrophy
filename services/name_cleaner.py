import re


def tr_lower(to_lower: str) -> str:
    spec = {"İ": "i", "I": "ı", "Ç": "ç"}
    for ch in spec:
        if ch in to_lower:
            to_lower.replace(ch, spec[ch])
    return to_lower.lower()


def clean_name(name: str) -> str:
    if not name:
        return ""

    name = (
        tr_lower(name)
            .replace("  ", " ")
            .replace("'", " ")
            .replace("-", "")
            .replace("é", "e")
            .replace(",", ".")
    )
    name = " ".join(name.strip().split())
    return name


pattern = re.compile(r'\s+')


def clean_for_sizing(s: str) -> str:
    if not s:
        return ""

    s = (s.lower()
         .replace("'", " ")
         .replace(",", ".")
         )
    s = re.sub(pattern, ' ', s)

    return s + " "
