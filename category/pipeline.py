import pathlib
from tqdm import tqdm
import itertools
from collections import defaultdict, Counter

from test.paths import get_path
import services
import constants as keys

cwd = pathlib.Path.cwd()
test_logs_dir = cwd / "test_logs"


def get_top_guesses(index, tokens):
    tokens_in_index = tuple(t for t in tokens if t in index)
    all_brands_or_cats_for_all_tokens = [index.get(t) for t in tokens]
    all_brands_or_cats_for_all_tokens = [set(c) for c in all_brands_or_cats_for_all_tokens if c]
    all_guesses = []
    for comb in itertools.combinations(all_brands_or_cats_for_all_tokens, 2):
        g = set.intersection(*comb)
        if g:
            all_guesses.append(list(g))

    candidates = services.flatten(all_guesses)
    # candidates = [c for c in candidates if all(t in c for t in tokens_in_index)]
    top_guess = None
    if all_guesses:
        top_guess = sorted(candidates, key=len)[0]
    if not top_guess and len(tokens_in_index) == 1:
        top_guess = tokens_in_index[0]

    return tokens_in_index, all_guesses, top_guess


def guess(sku, cat_index, brand_index):
    tokens = sku.get("name_freq").keys()
    doc = {key: sku[key] for key in ["clean_names"]}
    if "brand" not in sku:
        candidate_tokens, all_guesses, top_guess = get_top_guesses(
            brand_index, tokens
        )
        doc["brand_candidates"] = candidate_tokens
        doc["brand_all_guesses"] = all_guesses
        doc["top_brand_guess"] = top_guess

    if "cat" not in sku:
        candidate_tokens, all_guesses, top_guess = get_top_guesses(
            cat_index, tokens
        )
        doc["cat_candidates"] = candidate_tokens
        doc["cat_all_guesses"] = all_guesses
        doc["top_cat_guess"] = top_guess

    doc = {k: v for k, v in doc.items() if k and v}
    return doc


def add_cat_and_brand(full_skus):
    for sku_id, sku in tqdm(full_skus.items()):
        cats = sku.get(keys.CATEGORIES, [])

        subcats = [
            cat[-1].split("/")[-1]
            if isinstance(cat, list) else cat
            for cat in cats
        ]

        subcats = [services.clean_name(c).split() for c in subcats if c]
        subcats = services.flatten(subcats)

        brands = sku.get(keys.BRAND)
        clean_brands = [services.clean_name(b) for b in brands if b]

        clean_names = sku.get("clean_names")
        name_tokens = services.get_tokens_of_a_group(clean_names)

        sku.update(
            {
                "subcat_freq": Counter(subcats),
                "brand_freq": Counter(clean_brands),
                "name_freq": Counter(name_tokens),
            }
        )


if __name__ == "__main__":
    full_skus_path = get_path("may18/full_skus.json")
    full_skus = services.read_json(full_skus_path)
