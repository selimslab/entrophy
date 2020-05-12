import re
import unicodedata


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

    # only size can have .
    tokens = []
    for t in name.split():
        if not t.replace(".", "").isdigit():
            tokens.append(t.replace(".", " "))
        else:
            tokens.append(t)

    name = " ".join(tokens)

    remove_whitespace_pattern = re.compile(r"\s+")
    name = re.sub(remove_whitespace_pattern, " ", str(name)).strip()
    return name


if __name__ == "__main__":
    x = clean_name("eti̇ peti̇to")
    print(x)
