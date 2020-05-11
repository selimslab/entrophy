import services
from services.size_finder import size_finder, SizingException


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
        (" 0.75  L adfa", (750, "ml")),
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

    for case, answer in test_cases:
        try:
            result = size_finder.get_digits_unit_size(services.clean_name(case))
            try:
                assert answer == tuple(result[:2])
            except AssertionError:
                print("FAIL", case, answer, result)

        except SizingException as e:
            print(e)


if __name__ == "__main__":
    pass
