import os
from collections import Counter
import logging

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from tqdm import tqdm

import services
from paths import output_dir
from services.size_finder import size_finder
import constants as keys


def new_top_words(model, feature_names, n_top_words):
    top_words = (
        " ".join([feature_names[i] for i in topic.argsort()[: -n_top_words - 1: -1]])
        for topic_idx, topic in enumerate(model.components_)
    )
    return list(set(top_words))


def lda(sentences: list, n_gram=2, n_top_words=1):
    n_features = 800
    n_components = 7

    try:
        tf_vectorizer = CountVectorizer(max_features=n_features, ngram_range=(1, n_gram))
        tf_matrix = tf_vectorizer.fit_transform(sentences)
    except ValueError:
        return []

    lda = LatentDirichletAllocation(
        n_components=n_components,
        max_iter=20,
        learning_method="online",
        learning_offset=50.0,
        random_state=0,
    )
    lda.fit(tf_matrix)

    tf_feature_names = tf_vectorizer.get_feature_names()
    # topics = lda.transform(sentences[:3])
    # print(topics)

    return new_top_words(lda, tf_feature_names, n_top_words)


def filtered_sku_name_generator(tree: dict, token_brand_freq_by_subcat: dict) -> tuple:
    """

    a topic should be in multiple brands so remove a word if it's only in a single brand

    """
    logging.info("filtered_sku_name_generator..")
    for subcat, brands in tqdm(tree.items()):
        sku_name_strings_in_subcat = []
        for brand, names in brands.items():
            sku_tokens = services.tokenize_a_nested_list(names)
            sku_tokens = [t.strip() for t in sku_tokens if token_brand_freq_by_subcat[subcat].get(t, 0) > 1]
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


def remove_subcat_brand_barcode_from_clean_names(name, brand, subcat, brands_in_results):
    all_matches = size_finder.get_all_matches(name + " ")
    for match in all_matches:
        name = name.replace(match, "")

    name = name.replace(brand, "").replace(subcat, "")
    name_tokens = [
        n.strip() for n in name.split()
        if (
                n not in brands_in_results
                and len(n) > 2
                and not n.isdigit()
        )
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
                    remove_subcat_brand_barcode_from_clean_names(name, brand, subcat, brands_in_results)
                    for name in name_group
                ]
                names = [n for n in names if n]
                groups.append(names)

            tree[subcat][brand] = groups

    return tree


def clean_for_lda():
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


def nlp():
    clean_tree_path = output_dir / "clean_tree.json"
    if os.path.exists(clean_tree_path):
        clean_tree = services.read_json(clean_tree_path)
    else:
        logging.info("creating clean tree..")
        clean_tree = clean_for_lda()
        services.save_json(clean_tree_path, clean_tree)

    token_brand_freq_by_subcat = get_token_brand_freq_by_subcat(clean_tree)

    lda_topics = {}
    logging.info("creating topics..")
    for subcat, sku_name_strings_in_subcat in filtered_sku_name_generator(clean_tree, token_brand_freq_by_subcat):
        top_words = lda(sku_name_strings_in_subcat, n_gram=1, n_top_words=1)
        lda_topics[subcat] = top_words

    services.save_json(output_dir / "lda_topics.json", lda_topics)


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)
    nlp()
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
