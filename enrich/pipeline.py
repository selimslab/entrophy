from paths import *
from prepare_docs_to_guess import *
from guess import *


def add_cat_and_brand():
    """
    1. get raw brands from websites
    2. get raw categories from myo, c4, migros, ty, gratis, watsons, joker, civil
    3. create a big brand list and a big category list
    4. clean brands and cats
    5. create an inverted index for brands and cats
    token: [all brands which includes this token]
    eg.
    loreal paris -> loreal : [all brands which includes loreal],
    paris: [all brands which includes paris]
    6.
    """

    full_skus = services.read_json(full_skus_path)

    guess_docs = create_guess_docs(full_skus.values())

    services.save_json(guess_docs_path, guess_docs)

    brand_index = services.read_json(brand_index_path)
    cat_index = services.read_json(cat_index_path)

    select_brand(guess_docs, brand_index)
    select_cat(guess_docs, cat_index)

    docs_with_brand_and_cat = [
        services.filter_empty_or_null_dict_values(doc) for doc in guess_docs
    ]

    services.save_json(docs_with_brand_and_cat_path, docs_with_brand_and_cat)

    # stat(docs_with_brand_and_cat)


if __name__ == "__main__":
    ...
