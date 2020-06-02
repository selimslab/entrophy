import services
import collections
from pprint import pprint

import services.collections_util


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

    cat_tokens = services.tokenize_a_nested_list(
        services.collections_util.flatten(cats)
    )
    cat_token_freq = collections.Counter(cat_tokens)

    subcats = []
    for cat in cats:
        if isinstance(cat, list):
            subcats.append(cat[-1])
        else:
            subcats.append(cat)

    subcats = [sub.split("/")[-1] for sub in subcats]

    pprint(subcats)

    subcats = [services.clean_name(c).split() for c in subcats if c]
    subcats = services.collections_util.flatten(subcats)
    cat_freq = collections.Counter(subcats)

    pprint(cat_freq)

    pprint(cat_token_freq)
