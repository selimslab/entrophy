import re
from typing import List, Tuple

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


class SizingException(Exception):
    pass


class SizeFinder:
    def __init__(self):
        self.patterns = self.create_size_patterns()
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
                "".join((digit_pattern, unit_pattern))
                for digit_pattern in digit_patterns
            ]
            patterns.append(("|".join(pats), clean_unit))

        for (unit_pattern, clean_unit) in units:
            all_digits_pattern = " ".join(("\\d+", unit_pattern))
            patterns.append((all_digits_pattern, clean_unit))

            all_digits_pattern = "".join(("\\d+", unit_pattern))
            patterns.append((all_digits_pattern, clean_unit))

        return patterns

    @staticmethod
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

        """
        why multiple matches is a bad idea

        FAIL dasd 3 6.5 kg # dasd 3 6.5 kg # (6500, 'gr') # [(6500, 'gr', '6.5 kg'), (5000, 'gr', '5 kg')]

        FAIL  0.75 L adfa # 0.75 l adfa # (750, 'ml') # [(750, 'ml', '0.75 l'), (75000, 'ml', '75 l')]

        FAIL dasd 4 x 200 ML 565dfds # dasd 4 x 200 ml 565dfds # (800, 'ml') # [(800, 'ml', '4 x 200 ml'), (200, 'ml', '200 ml')]

        """

        for (pattern, unit) in self.patterns:
            matches = re.findall(pattern, to_be_matched)
            if matches:
                match = matches.pop(0).strip()
                return match, unit

    def get_digits_unit_size(self, name):
        name += " "
        match = self.pattern_match(name)
        if match:
            matched_string, unit = match
            digits = self.get_digits(matched_string)
            if digits and digits < self.max_digits.get(unit, 1000):
                digits, unit = self.convert(digits, unit)
                return digits, unit, matched_string


size_finder = SizeFinder()

if __name__ == "__main__":
    ...
