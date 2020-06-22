import logging
from typing import List
import itertools
import operator

from tqdm import tqdm

import services
import constants as keys
import paths as paths

from filter_names import add_filtered_names
from main import get_indexes

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.naive_bayes import MultinomialNB


def predict_subcat(products: List[dict]) -> list:
    """
    use products with subcat as training, and classify the remaining
    """
    if not products:
        return []

    with_sub = [
        p
        for p in products
        if keys.SUBCAT in p and p.get(keys.SUBCAT_SOURCE) != "global_name"
    ]
    no_sub = [
        p
        for p in products
        if keys.SUBCAT not in p or p.get(keys.SUBCAT_SOURCE) == "global_name"
    ]

    X_train = []
    y_train = []
    logging.info("training..")
    for product in tqdm(with_sub):
        names = product.get(keys.FILTERED_NAMES, [])
        sub = product.get(keys.SUBCAT)
        X_train += [" ".join(names)]
        y_train += [sub]

    filtered_names = [product.get(keys.FILTERED_NAMES, []) for product in tqdm(no_sub)]
    X_test = [" ".join(names) for names in filtered_names]

    if not X_train or not y_train or not X_test:
        return []

    count_vect = CountVectorizer()
    try:
        X_train_counts = count_vect.fit_transform(X_train)
    except ValueError:
        return []
    tfidf_transformer = TfidfTransformer()
    X_train_tfidf = tfidf_transformer.fit_transform(X_train_counts)
    clf = MultinomialNB().fit(X_train_tfidf, y_train)

    y_pred = clf.predict(count_vect.transform(X_test))

    for i, product in enumerate(no_sub):
        product[keys.SUBCAT] = y_pred[i]
        product[keys.SUBCAT_SOURCE] = "ML"

    for names, pred in zip(X_test, y_pred):
        print(names)
        print(pred)
        print()

    return no_sub


def group_by_brand(products):
    keyfunc = lambda product: product.get(keys.BRAND, "")
    products = sorted(products, key=keyfunc)
    for key, items in itertools.groupby(products, key=keyfunc):
        yield key, items


def run():
    products = services.read_json(paths.products_out)
    *rest, possible_subcats_by_brand = get_indexes(products)
    products = add_filtered_names(
        products, possible_subcats_by_brand, remove_subcat=False
    )
    relevant_keys = {
        keys.PRODUCT_ID,
        keys.SKU_ID,
        keys.FILTERED_NAMES,
        keys.SUBCAT,
        keys.SUBCAT_SOURCE,
        keys.CLEAN_NAMES,
        keys.BRAND,
    }
    products = [services.filter_keys(p, relevant_keys) for p in products]

    subcat_predicted = []
    for brand, products in group_by_brand(products):
        predicted = predict_subcat(list(products))
        subcat_predicted += predicted

    services.save_json("stage/ML_subcat_predicted.json", subcat_predicted)


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)
    run()
