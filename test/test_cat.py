import services
import collections
from pprint import pprint


def test_cat():
    cats = [
        ["Cipsler"],
        ["Cipsler"],
        ["CİPS & MISIR PATLAĞI"],
        "cips/atıştırmalık/gıda, şekerleme",
        ["Cips"],
        ["Algida Carte D'or Classic 925 ml Cips Hediye", "Cipsler"],
        ["Cipsler", "ATIŞTIRMALIK"],
        ["Cipsler"],
        ["Cipsler"],
        ["Cipsler"],
        ["Cipsler"],
    ]

    cat_tokens = services.get_tokens_of_a_group(services.flatten(cats))
    cat_token_freq = collections.Counter(cat_tokens)

    subcats = []
    for c in cats:
        if isinstance(c, list):
            subcat = c[-1].split("/")[-1]
            subcats.append(subcat)
        else:
            subcats.append(c)

    subcats = [services.clean_name(c).split() for c in subcats if c]
    subcats = services.flatten(subcats)
    cat_freq = collections.Counter(subcats)

    pprint(cat_freq)

    pprint(cat_token_freq)

