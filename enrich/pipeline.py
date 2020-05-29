import logging

from paths import *
from prepare_docs_to_guess import *
from guess import *
from index import get_brand_index, get_cat_index
from count_fields import stat


def add_cat_and_brand():
    """
    find brand first,
    there only a few possible cats for this brand
    indexes should reflect that too

    johnson s baby -> johnsons baby
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

    logging.info(f"{len(product_groups)}, product_groups")

    logging.info("adding cats and brands..")
    add_brand_and_cat(guess_docs, brand_index, cat_index, product_groups)

    docs_with_brand_and_cat = [
        services.filter_empty_or_null_dict_values(doc) for doc in guess_docs.values()
    ]
    services.save_json(
        output_dir / "docs_with_brand_and_cat.json", docs_with_brand_and_cat
    )

    summary_keys = {"brand", "cat", "clean_names"}
    summary_brand_and_cat = [
        services.filter_keys(doc, summary_keys) for doc in docs_with_brand_and_cat
    ]

    for doc in summary_brand_and_cat:
        doc["name"] = doc.pop("clean_names")[0]

    services.save_json(output_dir / "summary_brand_and_cat.json", summary_brand_and_cat)

    stat(docs_with_brand_and_cat)

    # TODO from clean brand to real brand


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)
    add_cat_and_brand()
    """
    hey brand could be easier 
    but we are treating it just the same? why?

    "bebek bezi/bebek, oyuncak"
    """
