import re
from services.size_util import (
    get_digits,
    create_size_patterns,
    convert_to_standard,
    max_digits,
)


class SizeFinder:
    def __init__(self):
        self.patterns = create_size_patterns()

    def get_first_match(self, s: str):
        """
        why multiple matches is a bad idea

        FAIL dasd 3 6.5 kg # dasd 3 6.5 kg # (6500, 'gr') # [(6500, 'gr', '6.5 kg'), (5000, 'gr', '5 kg')]

        FAIL  0.75 L adfa # 0.75 l adfa # (750, 'ml') # [(750, 'ml', '0.75 l'), (75000, 'ml', '75 l')]

        FAIL dasd 4 x 200 ML 565dfds # dasd 4 x 200 ml 565dfds # (800, 'ml') # [(800, 'ml', '4 x 200 ml'), (200, 'ml', '200 ml')]

        """
        s += " "
        for (pattern, unit) in self.patterns:
            matches = re.findall(pattern, s)
            if matches:
                match = matches.pop(0).strip()
                return match, unit

    def get_first_digits_unit(self, s):
        match_and_unit = self.get_first_match(s)
        if match_and_unit:
            match, unit = match_and_unit
            digits = get_digits(match)
            if digits and digits < max_digits.get(unit, 1000):
                digits, unit = convert_to_standard(digits, unit)
                return digits, unit

    def get_size_unit_tuples(self, s: str) -> list:
        """
        in "faf 750 gr 35 gr 56ml 2li "
        out ('faf', [('56ml', 'ml'), ('750 gr', 'gr'), ('35 gr', 'gr'), ('2li', 'adet')])

        """
        size_unit_tuples = []
        s += " "
        for (pattern, unit) in self.patterns:
            matched_size_patterns = re.findall(pattern, s)
            if matched_size_patterns:
                for size_pattern in matched_size_patterns:
                    size_pattern = size_pattern.strip()
                    s = s.replace(size_pattern, "")
                    size_unit_tuples.append((size_pattern, unit))
        return size_unit_tuples


size_finder = SizeFinder()


def test_remove_all_size_matches():
    case = " 750 gr faf 35 gr 56ml 2li "
    res = size_finder.get_size_unit_tuples(case)
    assert res == (
        "faf",
        [("56ml", "ml"), ("750 gr", "gr"), ("35 gr", "gr"), ("2li", "adet")],
    )


if __name__ == "__main__":
    test_remove_all_size_matches()
