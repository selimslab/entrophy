import re
from typing import List, Tuple

from services.sizing.digits_mixin import DigitsMixin
from .pattern_pairs import PAIRS
from .pattern_regexes import REGEXES


class SizingException(Exception):
    pass


class SizeFinder(DigitsMixin):
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

    def pattern_match(self, to_be_matched: str):
        for (pattern, unit) in self.patterns:
            match = re.findall(pattern, to_be_matched)
            if match:
                # print(pattern, to_be_matched)
                match = match.pop(0).strip()
                return match, unit

    def get_digits_and_unit(self, name):
        bad_tokens = {"+", "essence", "ruj", "aptamil 5"}
        if any([token in name for token in bad_tokens]):
            raise SizingException("bad sizing token")

        matched = self.pattern_match(name)
        if matched:
            match, unit = matched
            digits = self.get_digits(match, unit)
            if digits:
                if digits > self.max_digits.get(unit, 1000):
                    raise SizingException("anormal digits")
                if float(digits).is_integer():
                    digits = int(digits)

                digits, unit = self.convert(digits, unit)

                return digits, unit


size_finder = SizeFinder()
