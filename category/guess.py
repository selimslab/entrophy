from tqdm import tqdm
import itertools

import services.collections_util
import services


def get_top_guesses(index, tokens):
    tokens_in_index = tuple(t for t in tokens if t in index)
    index_values = [index.get(t) for t in tokens]
    index_values = [set(c) for c in index_values if c]
    all_guesses = []
    for comb in itertools.combinations(index_values, 2):
        g = set.intersection(*comb)
        if g:
            all_guesses.append(list(g))

    if not all_guesses:
        all_guesses = [list(v) for v in index_values]

    candidates = services.collections_util.flatten(all_guesses)

    top_guess = None
    if all_guesses:
        top_guess = sorted(candidates, key=len)[0]
    if not top_guess and len(tokens_in_index) == 1:
        top_guess = tokens_in_index[0]

    return tokens_in_index, all_guesses, top_guess


def select_cat_and_brand(guess_docs, brand_index, cat_index):
    for doc in tqdm(guess_docs):
        tokens = doc.get("name_freq").keys()

        if "brand_freq" in doc:
            doc["brand"] = services.get_most_frequent_key(doc.get("brand_freq"))
        else:
            candidate_tokens, all_guesses, top_guess = get_top_guesses(
                brand_index, tokens
            )
            doc["brand_candidates"] = candidate_tokens
            doc["brand_all_guesses"] = all_guesses
            doc["top_brand_guess"] = top_guess

        if "subcat_freq" in doc:
            doc["cat"] = services.get_most_frequent_key(doc.get("subcat_freq"))
        else:
            candidate_tokens, all_guesses, top_guess = get_top_guesses(
                cat_index, tokens
            )
            doc["cat_candidates"] = candidate_tokens
            doc["cat_all_guesses"] = all_guesses
            doc["top_cat_guess"] = top_guess

    docs_with_brand_and_cat = [
        services.filter_empty_or_null_dict_values(doc) for doc in guess_docs
    ]

    return docs_with_brand_and_cat
