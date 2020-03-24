import constants as keys
from services import name_cleaner, SizeFinder, SizingException


class SizeAdder:
    def __init__(self, sizer=SizeFinder()):
        self.sizer = sizer

    def add_size(self, item):
        name = item.get(keys.NAME, "")
        market = item.get(keys.MARKET)
        if name and market not in keys.HELPER_MARKETS:
            size_name = name_cleaner.size_cleaner(name)
            try:
                result = self.sizer.get_digits_and_unit(size_name)
                if result:
                    digits, unit = result
                    item[keys.DIGITS], item[keys.UNIT], item[keys.SIZE] = (
                        digits,
                        unit,
                        " ".join([str(digits), unit]),
                    )
            except SizingException:
                pass

        return item
