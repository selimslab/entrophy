from tqdm import tqdm
import itertools

import services


def generate_all_guesses(index, tokens):
    index_values = [index.get(t) for t in tokens]
    index_values = [set(c) for c in index_values if c]
    all_guesses = []
    for comb in itertools.combinations(index_values, 2):
        g = set.intersection(*comb)
        if g:
            all_guesses.append(list(g))

    if not all_guesses:
        all_guesses = [list(v) for v in index_values]

    return all_guesses


def get_top_guess(all_guesses, tokens_in_index):
    top_guess = None
    if all_guesses:
        candidates = services.flatten(all_guesses)
        top_guess = sorted(candidates, key=len)[0]
    if not top_guess and len(tokens_in_index) == 1:
        top_guess = tokens_in_index[0]

    return top_guess


def select_cat(guess_docs, cat_index):
    for doc in tqdm(guess_docs):
        tokens = doc.get("name_freq").keys()

        if "subcat_freq" in doc:
            doc["cat"] = services.get_most_frequent_key(doc.get("subcat_freq"))
        else:
            all_guesses = generate_all_guesses(cat_index, tokens)
            tokens_in_index = tuple(t for t in tokens if t in cat_index)
            top_guess = get_top_guess(all_guesses, tokens_in_index)
            doc["cat_candidates"] = tokens_in_index
            doc["cat_guesses"] = all_guesses
            doc["cat"] = top_guess


def select_brand(guess_docs, brand_index):
    for doc in tqdm(guess_docs):

        tokens = doc.get("name_freq").keys()

        if "brand_freq" in doc:
            doc["brand"] = services.get_most_frequent_key(doc.get("brand_freq"))
        else:
            # a more frequent token should be a more relwvant guess
            all_guesses = generate_all_guesses(brand_index, tokens)
            tokens_in_index = tuple(t for t in tokens if t in brand_index)
            top_guess = get_top_guess(all_guesses, tokens_in_index)

            doc["brand_candidates"] = tokens_in_index
            doc["brand_guesses"] = all_guesses
            doc["brand"] = top_guess


def select_cat_weighted(guess_docs, cat_index):
    pass


def select_brand_weighted(guess_docs, brand_index):
    pass
