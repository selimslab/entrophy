import re
from typing import List, Tuple

REGEXES = [
    "\\d+\\.\\d+",
    "\\d+x\\d+",
    "\\d+ x \\d+",
    "\\d+x \\d+",
    "\\d+ x\\d+",
    "\\d+\\*\\d+",
    "\\d+\\ * \\d+",
    "\\d+\\* \\d+",
    "\\d+\\ *\\d+",
    "\\d+",
]

PAIRS = [
    ("yıkama", "yıkama"),
    ("tablet", "tablet"),
    ("kapsül", "tablet"),
    ("litre", "lt"),
    ("tane", "adet"),
    ("adet", "adet"),
    ("ml", "ml"),
    ("cc", "ml"),
    ("cl", "cl"),
    ("lt", "lt"),
    ("gr", "gr"),
    ("kg", "kg"),
    ("mg", "mg"),
    ("lı", "adet"),
    ("li", "adet"),
    ("lu", "adet"),
    ("lü", "adet"),
    ("g", "gr"),
    ("l", "lt"),
]


class SizingException(Exception):
    pass


class SizeFinder:
    def __init__(self):
        self.patterns = self.create_size_patterns(PAIRS, REGEXES)
        self.max_digits = {
            "yıkama": 100,
            "tablet": 400,
            "adet": 1000,
            "lt": 100,
            "kg": 100,
            "gr": 40000,
            "ml": 40000,
            "cl": 10000,
        }

    @staticmethod
    def create_size_patterns(
            pair_list: List[Tuple[str, str]], regex_list: List[str]
    ) -> List[Tuple[str, str]]:

        patterns = list()
        for (search_term, unit) in pair_list:
            # " 30 ml"
            pats = [" " + " ".join((reg, search_term)) + " " for reg in regex_list]
            patterns.append(("|".join(pats), unit))

            # " 30ml"
            pats = ["".join((" ", reg, search_term)) + " " for reg in regex_list]
            patterns.append(("|".join(pats), unit))

        for (search_term, unit) in pair_list:
            # "30ML"
            pats = ["".join((reg, search_term)) + " " for reg in regex_list]
            patterns.append(("|".join(pats), unit))

            # "30 ml"
            pats = [" ".join((reg, search_term)) + " " for reg in regex_list]
            patterns.append(("|".join(pats), unit))

        return patterns

    @staticmethod
    def get_digits(match: str, unit: str):
        digits_list = re.findall(r"\d+", match)
        if not digits_list:
            return

        if len(digits_list) == 1:
            return float(digits_list.pop())
        elif len(digits_list) == 2 and ("x" in match or "*" in match):
            digits = float(digits_list[0]) * float(digits_list[1])
            return digits

        else:
            if unit in {"adet", "yıkama", "tablet"}:
                digits = digits_list[-1]
            else:
                digits = ".".join([str(digit) for digit in digits_list])

            return float(digits)

    @staticmethod
    def convert(digits, unit):
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


    def pattern_match(self, to_be_matched: str):
        for (pattern, unit) in self.patterns:
            match = re.findall(pattern, to_be_matched)
            if match:
                # print(pattern, to_be_matched)
                match = match.pop(0).strip()
                return match, unit

    def get_digits_unit_size(self, name):
        name += " "
        matched = self.pattern_match(name)
        if matched:
            match, unit = matched
            digits = self.get_digits(match, unit)
            if digits:
                if digits > self.max_digits.get(unit, 1000):
                    raise SizingException(f"anormal digits in {name}")
                if float(digits).is_integer():
                    digits = int(digits)

                digits, unit = self.convert(digits, unit)

                return digits, unit, match

        raise SizingException(f"no size found in {name}")


size_finder = SizeFinder()
