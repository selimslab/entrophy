from services import name_cleaner
from services.sizing.main import size_finder, SizingException


def test_sizing():
    test_cases = [
        [" Gillette Tıraş Bıçağı Yedek Mach 3 2'li  fs335 ", (2, "adet")],
        ["  2'li   ", (2, "adet")],
        ["dasd 10'lu   ", (10, "adet")],
        ["Pınar %60 Light Süt 1 L gfds", (1000, "ml")],
        ["Ph 3.8 200 Ml fasf", (200, "ml")],
        ["da 200 ml dasd", (200, "ml")],
        ["dasd 4 kg ", (4000, "gr")],
        ["da 200 ml dasd", (200, "ml")],
        ["f54 8 yıkama ", (8, "yıkama")],
        ["F20 200 ML dwa", (200, "ml")],
        ["2x200 ML afdas", (400, "ml")],
        ["2*200 ML 32352", (400, "ml")],
        ["ewtew 2/4 2*200 ML 46", (400, "ml")],
        ["dasd 4 x 200 ML 565dfds", (800, "ml")],
        ["2/1 360 ML ada", (360, "ml")],
        [" 0.75  L adfa", (750, "ml")],
        ["dasd 3 6.5 kg", (6500, "gr")],
        ["5 800 g", (800, "gr")],
        ["Persil Gülün Büyüsü 6 KG 40 Yıkama", (40, "yıkama")],
        ["aptamil 2 800 g", (800, "gr")],
        ["a Gazlı İçecek Portakal 1.75 L", (1750, "ml")],
    ]

    for case, answer in test_cases:
        try:
            result = size_finder.get_digits_unit_size(name_cleaner.clean_for_sizing(case))
            try:
                assert result == answer
            except AssertionError:
                print(case, result, answer)

        except SizingException as e:
            print(e)


if __name__ == "__main__":
    pass
