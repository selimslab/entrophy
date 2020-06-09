import os
from collections import Counter
import logging

from tqdm import tqdm

import services
from paths import output_dir
from services.size_finder import size_finder
import constants as keys

from topic_modelling import lda


def filtered_sku_name_generator(tree: dict, token_brand_freq_by_subcat: dict, sub_freq: dict) -> tuple:
    """

    a topic should be in multiple brands so remove a word if it's only in a single brand

    """
    logging.info("filtered_sku_name_generator..")
    for subcat, brands in tqdm(tree.items()):
        sku_name_strings_in_subcat = []
        for brand, name_groups in brands.items():
            for names in name_groups:
                sku_tokens = services.tokenize_a_nested_list(names)
                sku_tokens = [
                    t.strip()
                    for t in sku_tokens
                    if (token_brand_freq_by_subcat[subcat].get(t, 0) >= 2
                        and sub_freq[subcat].get(t, 0) >= 4)
                ]
                all_names_for_this_sku = " ".join(sku_tokens)
                if all_names_for_this_sku:
                    sku_name_strings_in_subcat.append(all_names_for_this_sku)

        if not sku_name_strings_in_subcat:
            continue
        if len(sku_name_strings_in_subcat) < 2:
            continue

        yield subcat, sku_name_strings_in_subcat


def create_sub_tree(skus_with_brand_and_sub_cat):
    """cat: { sub_cat : { type: {brand: {sub_brand : [products] } }"""

    tree = {}
    logging.info("create_sub_tree..")

    for sku in tqdm(skus_with_brand_and_sub_cat):
        brand, subcat = sku.get(keys.BRAND), sku.get(keys.SUBCAT)
        if brand and subcat:
            if subcat not in tree:
                tree[subcat] = {}
            if brand not in tree[subcat]:
                tree[subcat][brand] = []
            tree[subcat][brand].append(sku.get(keys.CLEAN_NAMES, []))

    return tree


def remove_subcat_brand_barcode_from_clean_names(
        name, brand, subcat, brands_in_results
):
    all_matches = size_finder.get_all_matches(name + " ")
    for match in all_matches:
        name = name.replace(match, "")

    name = name.replace(brand, "").replace(subcat, "")
    name_tokens = [
        n.strip()
        for n in name.split()
        if (n not in brands_in_results and len(n) > 2 and not n.isdigit())
    ]

    name = " ".join(name_tokens)

    return name


def remove_known(tree: dict, brands_in_results):
    """ remove subcat, brand, size """

    for subcat, brands in tqdm(tree.items()):

        for brand, clean_names in brands.items():
            groups = []
            for name_group in clean_names:
                names = [
                    remove_subcat_brand_barcode_from_clean_names(
                        name, brand, subcat, brands_in_results
                    )
                    for name in name_group
                ]
                names = [n for n in names if n]
                groups.append(names)

            tree[subcat][brand] = groups

    return tree


def create_clean_tree():
    """
    remove barcodes, all sizes, subcats, brands, gender, color, cat, ...
    """
    skus_with_brand_and_sub_cat = services.read_json(
        output_dir / "skus_with_brand_and_sub_cat.json"
    )

    sub_tree = create_sub_tree(skus_with_brand_and_sub_cat)
    services.save_json(output_dir / "sub_tree.json", sub_tree)

    brands_in_results = services.read_json(output_dir / "brands_in_results.json")
    brands_in_results = set(brands_in_results)
    brands_in_results = brands_in_results.difference({"domates", "biber"})

    clean_tree = remove_known(sub_tree, brands_in_results)

    return clean_tree


def get_token_brand_freq_by_subcat(tree):
    """ in how many brands of a subcat, a token is present """
    token_brand_freq_by_subcat = {}

    for subcat, brands in tqdm(tree.items()):
        tokensets = []
        for brand, names in brands.items():
            all_tokens = services.tokenize_a_nested_list(names)
            tokensets += list(set(all_tokens))
        token_brand_freq_by_subcat[subcat] = Counter(tokensets)

    return token_brand_freq_by_subcat


def count_tokens_by_subcat(clean_tree):
    sub_freq = {}

    for sub, brands in clean_tree.items():
        names = [list(set(services.tokenize_a_nested_list(names))) for brand, names in brands.items()]
        name_tokens = services.flatten(names)
        freq = {token: count for token, count in dict(Counter(name_tokens)).items() if count >= 5}
        sub_freq[sub] = freq

    return sub_freq


def create_input():
    clean_tree_path = output_dir / "clean_tree.json"
    if os.path.exists(clean_tree_path):
        clean_tree = services.read_json(clean_tree_path)
    else:
        logging.info("creating clean tree..")
        clean_tree = create_clean_tree()
        services.save_json(clean_tree_path, clean_tree)

    token_brand_freq_by_subcat = get_token_brand_freq_by_subcat(clean_tree)
    sub_freq = count_tokens_by_subcat(clean_tree)
    services.save_json(output_dir / "sub_freq.json", sub_freq)

    input_names = {}
    for subcat, sku_names_in_subcat in filtered_sku_name_generator(
            clean_tree, token_brand_freq_by_subcat, sub_freq
    ):
        input_names[subcat] = sku_names_in_subcat
    return input_names


def create_topics():
    input_names = create_input()
    services.save_json(output_dir / "lda_input_names.json", input_names)

    lda_topics = {}
    logging.info("creating topics..")
    for subcat, sku_names_in_subcat in tqdm(input_names.items()):
        top_words = lda(sku_names_in_subcat, n_gram=2, n_top_words=1)
        top_words = [t for t in top_words if not len(t.split()) > 1 and len(set(t.split())) == 1]
        lda_topics[subcat] = top_words

    services.save_json(output_dir / "lda_topics22.json", lda_topics)


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)
    create_topics()
    """
    plan 

    * merge similar brands
        loreal paris -> loreal 

    * remove all sizes 

    * Buraya sku'lar ile değil de product group ile girsek mantıklı olmaz mı 

    * remove barcodes  ok

    remove brands ok 

    filter len(token)<3 

    a topic should be in multiple brands  ok 
    """
