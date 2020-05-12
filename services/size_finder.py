import re
from typing import List, Tuple

digit_patterns = [
    "\\d+\\.\\d+",
    "\\d+x\\d+",
    "\\d+ x \\d+",
    "\\d+x \\d+",
    "\\d+ x\\d+",  # 3 x 5
]

#  "\\d+\\ * \\d+",  # 3 * 5


units = [
    ("yıkama ", "yikama"),
    ("tablet ", "tablet"),
    ("kapsül ", "tablet"),
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

        """
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
        """

        return patterns

    @staticmethod
    def get_digits(match: str):
        allowed_chars = re.compile("[^0-9.*x]")
        digits = allowed_chars.sub("", match)

        # handle 2x6 4*20
        if "x" in digits:
            digits = digits.split("x")
        elif "*" in digits:
            digits = digits.split("*")
        try:
            if isinstance(digits, list) and len(digits) == 2:
                digits = float(digits[0]) * float(digits[1])
            digits = float(digits)
        except (TypeError, ValueError) as e:
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
        for (pattern, unit) in self.patterns:
            match = re.findall(pattern, to_be_matched)

            if match:
                match = match.pop(0).strip()
                return match, unit

    def get_digits_unit_size(self, name):
        name += " "
        matched = self.pattern_match(name)
        if matched:
            match, unit = matched
            digits = self.get_digits(match)
            if digits:
                if digits > self.max_digits.get(unit, 1000):
                    raise SizingException(f"anormal digits in {name}")

                digits, unit = self.convert(digits, unit)

                return digits, unit, match

        raise SizingException(f"no size found in {name}")


size_finder = SizeFinder()


def test_sizing():
    test_cases = (
        (" Gillette Tıraş Bıçağı Yedek Mach 3 2'li  fs335 ", (2, "adet")),
        ("  2'li   ", (2, "adet")),
        ("dasd 10'lu   ", (10, "adet")),
        ("Pınar %60 Light Süt 1 L gfds", (1000, "ml")),
        ("Ph 3.8 200 Ml fasf", (200, "ml")),
        ("da 200 ml dasd", (200, "ml")),
        ("dasd 4 kg ", (4000, "gr")),
        ("da 200 ml dasd", (200, "ml")),
        ("f54 8 yıkama ", (8, "yıkama")),
        ("F20 200 ML dwa", (200, "ml")),
        ("2x200 ML afdas", (400, "ml")),
        ("2*200 ML 32352", (400, "ml")),
        ("ewtew 2/4 2*200 ML 46", (400, "ml")),
        ("dasd 4 x 200 ML 565dfds", (800, "ml")),
        ("2/1 360 ML ada", (360, "ml")),
        (" 0.75 L adfa", (750, "ml")),
        ("dasd 3 6.5 kg", (6500, "gr")),
        ("5 800 g", (800, "gr")),
        ("Persil Gülün Büyüsü 6 KG 40 Yıkama", (40, "yıkama")),
        ("aptamil 2 800 g", (800, "gr")),
        ("a Gazlı İçecek Portakal 1.75 L", (1750, "ml")),
        ("780GR 4 LÜ", (780, "gr")),
        ("dasd 4 LU 780 GR asasd", (780, "gr")),
        ("süt 1/1 litre sadsad", (1000, "ml")),
        ("coca cola 1 lt.light", (1000, "ml")),
        ("ULKER 117 175GR PETIBOR ", (175, "gr")),
        ("5 800 gr. asdas", (800, "gr")),
        (" 0.75  L. adfa", (750, "ml")),
        (" 750 ml. adfa", (750, "ml")),
        ("30+ 50 ML", (50, "ml")),
    )

    import services

    for case, answer in test_cases:
        try:
            clean_name = services.clean_name(case)
            result = size_finder.get_digits_unit_size(clean_name)
            try:
                assert answer == tuple(result[:2])
            except (AssertionError, AttributeError) as e:
                print("FAIL", case, "#", clean_name, "#", answer, "#", result)
                print(e)

        except SizingException as e:
            print(e)


if __name__ == "__main__":
    test_sizing()
