import re


def join_digits_units(digits, unit):
    if not (digits and unit):
        return
    return " ".join([str(digits), unit])


# the order is important for patterns and units
digit_patterns = [
    "\\d+\\.\\d+",
    "\\d+x\\d+",
    "\\d+ x \\d+",
    "\\d+x \\d+",
    "\\d+ x\\d+",  # 3 x 5
]

#  "\\d+\\ * \\d+",  # 3 * 5


units = [
    ("yikama ", "yıkama"),
    ("tablet ", "tablet"),
    ("kapsul ", "tablet"),
    ("litre ", "lt"),
    ("tane ", "adet"),
    ("adet ", "adet"),
    ("ml ", "ml"),
    ("cc ", "ml"),
    ("cl ", "cl"),
    ("lt ", "lt"),
    ("gr ", "gr"),
    ("kg ", "kg"),
    ("mg ", "mg"),
    ("li ", "adet"),
    ("lu ", "adet"),
    ("g ", "gr"),
    ("l ", "lt"),
]


def create_size_patterns():
    patterns = []
    # "1 12.5 lt" => first look for 2.3
    for (unit_pattern, clean_unit) in units:
        # "30 ml "
        pats = [
            # create regex groups
            " ".join((digit_pattern, unit_pattern))
            for digit_pattern in digit_patterns
        ]
        # create a single regex to match 10x faster
        patterns.append(("|".join(pats), clean_unit))

    for (unit_pattern, clean_unit) in units:
        # "30ml"
        pats = [
            "".join((digit_pattern, unit_pattern)) for digit_pattern in digit_patterns
        ]
        patterns.append(("|".join(pats), clean_unit))

    for (unit_pattern, clean_unit) in units:
        all_digits_pattern = " ".join(("\\d+", unit_pattern))
        patterns.append((all_digits_pattern, clean_unit))

        all_digits_pattern = "".join(("\\d+", unit_pattern))
        patterns.append((all_digits_pattern, clean_unit))

    return patterns


def get_digits(match: str):
    allowed_chars = re.compile("[^0-9.x]")
    digits = allowed_chars.sub("", match)

    # handle 2x6
    try:
        if "x" in digits:
            digits = digits.split("x")
            digits = float(digits[0]) * float(digits[1])
        digits = float(digits)
    except (TypeError, IndexError, ValueError) as e:
        print(e)
        return

    return digits


def convert_to_standard(digits, unit):
    if unit == "kg":
        unit = "gr"
        digits = digits * 1000

    if unit == "cl":
        unit = "ml"
        digits = digits * 10

    if unit == "lt":
        unit = "ml"
        digits = digits * 1000

    if float(digits).is_integer():
        digits = int(digits)

    return digits, unit
