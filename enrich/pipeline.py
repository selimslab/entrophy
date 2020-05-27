from paths import *
from prepare_docs_to_guess import *
from guess import *
from index import get_brand_index, get_cat_index
from count_fields import get_name_freq, stat


def add_cat_and_brand():
    """
    1. get raw brands from websites
    2. get raw categories from
     myo, c4, migros, ty, gratis, watsons, joker, civil
    3. create a big brand list and a big category list
    4. clean brands and cats
    5. create an inverted index for brands and cats
    token: [all brands which includes this token]
    eg.
    loreal paris -> loreal : [all brands which includes loreal],
    paris: [all brands which includes paris]
    6.
    """

    full_skus = services.read_json(input_dir / "full_skus.json")

    # why unused ?
    name_freq = get_name_freq(full_skus)
    services.save_json(output_dir / "name_freq.json", name_freq)

    guess_docs = create_guess_docs(full_skus.values())
    services.save_json(output_dir / "guess_docs.json", guess_docs)

    brand_index = get_brand_index()
    cat_index = get_cat_index()
    select_brand(guess_docs, brand_index)
    select_cat(guess_docs, cat_index)

    docs_with_brand_and_cat = [
        services.filter_empty_or_null_dict_values(doc)
        for doc in guess_docs
    ]
    services.save_json(
        output_dir / "docs_with_brand_and_cat.json",
        docs_with_brand_and_cat)

    summary_keys = {
        "brand", "cat",
        "clean_names"
    }
    summary_brand_and_cat = [services.filter_keys(doc, summary_keys)
                             for doc in docs_with_brand_and_cat]

    for doc in summary_brand_and_cat:
        doc["name"] = doc.pop("clean_names")[0]

    services.save_json(
        output_dir / "summary_brand_and_cat.json",
        summary_brand_and_cat)

    stat(docs_with_brand_and_cat)

    # TODO from clean brand to real brand


if __name__ == "__main__":
    add_cat_and_brand()
