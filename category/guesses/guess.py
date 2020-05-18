import services
from collections import defaultdict
from tqdm import tqdm
import itertools
from index import create_indexes


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


def tree():
    return defaultdict(tree)


guess_tree = tree()

brand_guess = []
cat_guess = []


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


def clean_groups():
    groups = services.read_json("../groups.json")
    cat_index = services.read_json("../indexes/cat_index.json")
    brand_index = services.read_json("../indexes/brand_index.json")
    clean_groups = []

    for product_id, skus in tqdm(groups.items()):
        for sku_id, sku in skus.items():
            if "cat" not in sku or "brand" not in sku:
                doc = guess(sku, cat_index, brand_index)
                guess_tree[product_id][sku_id] = doc
                if "cat_candidates" in doc or "brand_candidates" in doc:
                    clean_groups.append(doc)
                if "top_cat_guess" in doc:
                    cat_guess.append(doc)
                if "top_brand_guess" in doc:
                    brand_guess.append(doc)

    services.save_json("guess.json", dict(guess_tree))
    services.save_json("cat_guess.json", cat_guess)
    services.save_json("brand_guess.json", brand_guess)
    services.save_json("../cleaner/clean_groups.json", clean_groups)


def go():
    # create_indexes()
    clean_groups()


if __name__ == "__main__":
    go()
