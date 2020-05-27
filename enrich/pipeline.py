import logging

from paths import *
from prepare_docs_to_guess import *
from guess import *
from index import get_brand_index, get_cat_index
from count_fields import stat


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


    uidelines

1. Be sure
2. True or nothing

Input is the brands and cats coming from markets

Almost all skus has multiple docs so there are multiple brand and cat possibilities for an sku

In this case how to be sure that a given brand or cat is correct ?

Correct brand is ok
 "correct category"  is fuzzy

there is no exact way, however there are a few helpful things

1. Different vendors, same info

if multiple docs of an SKU has the same brand or cat, this is probably correct, since it is rare for two independent vendors to agree on the same incorrect info

2. Name tokens

a brand or category is a word or words

so when you look at the cleaned names of an  sku, this gives a set of possible cats and brands for this SKU

then we can use these sets to decide

3. In group lookups

members of product groups can create a cleaner set of possibilities

4. Frequencies

every token, brand, cat, and name has a freq for the SKU, product group, and global

these freqs can be helpful to select

5. Indexes
given a name, how do you know what are the possible cats or brands for this name?

an index of token, candidates pairs is an easy way

so for every token you get some possible cat or brand, and when you intersect them you get the candidate for the name

This intersection is tricky, maybe a better way is to search every brand and cat in every name

another issue is stemming, partial matching may help here, but it is hard to decide how partial

How to select a brand or cat ?

1. algo1

if single brand in sku, select it

If multiple brands, select the globally most frequent one

if no brand, tokenize name, search tokens in brand index,
for every token comes a candidate set,
Intersect candidate sets by combinations of two,
Select the most common,
if not, select the shortest candidate


2. algorithm 2

Do not readily accept a cat, look at all possibilities first

for all the name tokens get possible cats and brands

this results in a large set of candidates

Brands and cats in SKU get more weight than others






After all most of these selections are guesses only



    """

    full_skus = services.read_json(input_dir / "full_skus.json")

    logging.info("indexing..")
    brands = [sku.get(keys.BRAND) for sku in full_skus.values()]
    brand_index = get_brand_index(brands)
    cats = [sku.get(keys.CATEGORIES) for sku in full_skus.values()]
    cat_index = get_cat_index(cats)

    logging.info("preparing..")
    guess_docs = create_guess_docs(full_skus)
    services.save_json(output_dir / "guess_docs.json", guess_docs)

    product_groups = defaultdict(set)
    for doc in guess_docs.values():
        if keys.PRODUCT_ID in doc:
            product_groups[doc.get(keys.PRODUCT_ID)].add(keys.SKU_ID)

    logging.info("selecting cats..")
    select_brand(guess_docs, brand_index, product_groups)
    select_cat(guess_docs, cat_index, product_groups)

    docs_with_brand_and_cat = [
        services.filter_empty_or_null_dict_values(doc)
        for doc in guess_docs.values()
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
    logging.getLogger().setLevel(logging.DEBUG)
    add_cat_and_brand()
