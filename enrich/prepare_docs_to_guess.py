from tqdm import tqdm
from collections import defaultdict
import services.collections_util
import services
import constants as keys
import multiprocessing


def get_the_guess_doc(sku):
    cats = sku.get(keys.CATEGORIES, [])
    clean_cats = services.clean_list_of_strings(services.flatten(cats))
    cat_token_freq = services.get_ordered_token_freq_of_a_nested_list(cats)

    subcats = []
    for cat in cats:
        if isinstance(cat, list):
            subcats.append(cat[-1])
        else:
            subcats.append(cat)

    subcats = [sub.split("/")[-1] for sub in subcats]
    subcat_token_freq = services.get_ordered_token_freq_of_a_nested_list(subcats)

    brands = sku.get(keys.BRAND)
    clean_brands = services.clean_list_of_strings(services.flatten(brands))
    brand_token_freq = services.get_ordered_token_freq_of_a_nested_list(brands)

    clean_names = sku.get("clean_names")
    name_token_freq = services.get_ordered_token_freq_of_a_nested_list(clean_names)

    guess_doc = {
        "clean_names": clean_names,
        "cats": cats,
        "clean_cats": clean_cats,
        "subcats": subcats,
        "brands": brands,
        "clean_brands": clean_brands,
        "cat_token_freq": cat_token_freq,
        "subcat_token_freq": subcat_token_freq,
        "brand_token_freq": brand_token_freq,
        "name_token_freq": name_token_freq,
        keys.SKU_ID: sku.get(keys.SKU_ID),
        keys.PRODUCT_ID: sku.get(keys.PRODUCT_ID),
    }

    return guess_doc


def create_guess_docs(full_skus: dict) -> dict:
    print("creating guess docs..")

    with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
        guess_docs = pool.map(get_the_guess_doc, tqdm(full_skus.values()))

    guess_docs = {
        doc.get(keys.SKU_ID): services.filter_empty_or_null_dict_values(doc)
        for doc in guess_docs
    }

    return guess_docs
