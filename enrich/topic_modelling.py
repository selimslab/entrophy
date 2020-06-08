from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation

from paths import output_dir
from tqdm import tqdm

import services

from services.size_finder import size_finder
import constants as keys


def new_top_words(model, feature_names, n_top_words):
    top_words = (
        " ".join([feature_names[i] for i in topic.argsort()[: -n_top_words - 1: -1]])
        for topic_idx, topic in enumerate(model.components_)
    )
    return list(set(top_words))


def lda(sentences: list, n_gram=1, n_top_words=1):
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


def sku_name_generator(tree: dict):
    for subcat, brands in tqdm(tree.items()):
        sku_name_strings_in_subcat = []
        for brand, names in brands.items():
            sku_tokens = services.tokenize_a_nested_list(names)
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
            stripped_groups = []
            for name_group in clean_names:
                stripped_names = []
                for name in name_group:
                    stripped_name = remove_subcat_brand_barcode_from_clean_names(name, brand, subcat, brands_in_results)
                    stripped_names.append(stripped_name)

                stripped_groups.append(stripped_names)

            tree[subcat][brand] = stripped_groups

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

    services.save_json(output_dir / "clean_tree.json", clean_tree)

    return clean_tree


def get_lda_topics(tree):
    lda_topics = {}
    for subcat, sku_name_strings_in_subcat in sku_name_generator(tree):
        top_words = lda(sku_name_strings_in_subcat)
        lda_topics[subcat] = top_words
    return lda_topics


def nlp():
    clean_tree = clean_for_lda()
    lda_topics = get_lda_topics(clean_tree)
    services.save_json(output_dir / "lda_topics.json", lda_topics)


if __name__ == "__main__":
    nlp()
    """
    plan 
    
    * merge similar brands
        loreal paris -> loreal 
    
    * remove all sizes 
    
    1. remove barcodes 
    to do this sku_ids shuold be present 
    
    2. remove brands
    
    3. filter len(token)<3
    
    4. 
    """
