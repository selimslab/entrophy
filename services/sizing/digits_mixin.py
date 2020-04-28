import re


class DigitsMixin:
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
