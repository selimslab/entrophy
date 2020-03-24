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
        .replace("'", "")
        .replace("-", "")
        .replace("é", "e")
        .replace("'", " ")
        .replace(",", ".")
    )
    name = " ".join(name.strip().split())
    return name


def size_cleaner(s: str) -> str:
    return clean_name(s) + " "
