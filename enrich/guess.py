from tqdm import tqdm
import itertools

import services
import constants as keys


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


def get_cat_metadata(doc, cat_index):
    cat_metadata = {}
    if "subcat_freq" in doc:
        cat_metadata["cat"] = services.get_most_frequent_key(doc.get("subcat_token_freq"))
    else:
        name_tokens = doc.get("name_token_freq").keys()
        all_guesses = generate_all_guesses(cat_index, name_tokens)
        tokens_in_index = tuple(t for t in name_tokens if t in cat_index)
        top_guess = get_top_guess(all_guesses, tokens_in_index)
        cat_metadata["cat_candidates"] = tokens_in_index
        cat_metadata["cat_guesses"] = all_guesses
        cat_metadata["cat"] = top_guess

    return cat_metadata


def get_brand_metadata(doc, brand_index):
    brand_metadata = {}
    if "brand_freq" in doc:
        brand_metadata["brand"] = services.get_most_frequent_key(doc.get("brand_token_freq"))
    else:
        name_tokens = doc.get("name_token_freq").keys()
        # a more frequent token should be a more relevant guess
        all_guesses = generate_all_guesses(brand_index, name_tokens)
        tokens_in_index = tuple(t for t in name_tokens if t in brand_index)
        top_guess = get_top_guess(all_guesses, tokens_in_index)

        brand_metadata["brand_candidates"] = tokens_in_index
        brand_metadata["brand_guesses"] = all_guesses
        brand_metadata["brand"] = top_guess
    return brand_metadata


def look_brand_in_group(docs):
    ...


def look_cat_in_group(docs):
    ...


def add_brand_and_cat(guess_docs, brand_index, cat_index, product_groups):
    for pid, sku_ids in product_groups.items():
        docs = [guess_docs.get(sku_id) for sku_id in sku_ids]
        brand = look_brand_in_group(docs)
        cat = look_cat_in_group(docs)
        for sku_id in sku_ids:
            guess_docs[sku_id]["brand"] = brand
            guess_docs[sku_id]["cat"] = cat

    for id, doc in tqdm(guess_docs.items()):
        if keys.PRODUCT_ID in doc:
            # already processed above
            continue
        brand_metadata = get_brand_metadata(doc, brand_index)
        doc.update(brand_metadata)

        cat_metadata = get_cat_metadata(doc, cat_index)
        doc.update(cat_metadata)


def select_cat_weighted(guess_docs, cat_index):
    pass


def select_brand_weighted(guess_docs, brand_index):
    pass
