from typing import List, Dict


def count_fields(docs: List[Dict], target_key):
    return sum(1 if target_key in doc else 0 for doc in docs)


def stat(docs):
    """ how many is guessed ? """
    with_brand = count_fields(docs, "brand")
    with_cat = count_fields(docs, "cat")

    with_brand_guess = count_fields(docs, "top_brand_guess")
    with_cat_guess = count_fields(docs, "top_cat_guess")

    print(
        with_brand, with_brand_guess, with_cat, with_cat_guess,
    )
