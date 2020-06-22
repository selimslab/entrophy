import logging
from typing import List
import itertools
import operator

from tqdm import tqdm

import services
import constants as keys
import paths as paths

from filter_names import add_filtered_names

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.naive_bayes import MultinomialNB


def classify_subcat():
    """
    use products with subcat as training, and classify the remaining
    """
    products = services.read_json(paths.products_out)
    products = add_filtered_names(products, remove_subcat=False)
    relevant_keys = {keys.FILTERED_NAMES, keys.SUBCAT, keys.CLEAN_NAMES, keys.BRAND}
    products = [services.filter_keys(p, relevant_keys) for p in products]

    with_sub = [p for p in products if keys.SUBCAT in p]
    no_sub = [p for p in products if keys.SUBCAT not in p]

    X_train = []
    y_train = []
    logging.info("training..")
    for product in tqdm(with_sub):
        names = product.get(keys.FILTERED_NAMES, [])
        sub = product.get(keys.SUBCAT)
        X_train += [" ".join(names)]
        y_train += [sub]

    count_vect = CountVectorizer()
    X_train_counts = count_vect.fit_transform(X_train)
    tfidf_transformer = TfidfTransformer()
    X_train_tfidf = tfidf_transformer.fit_transform(X_train_counts)
    clf = MultinomialNB().fit(X_train_tfidf, y_train)

    filtered_names = [product.get(keys.FILTERED_NAMES, []) for product in tqdm(no_sub)]
    X_test = [" ".join(names) for names in filtered_names]
    y_pred = clf.predict(count_vect.transform(X_test))

    for i, product in enumerate(no_sub):
        product[keys.SUBCAT] = y_pred[i]
        product[keys.SUBCAT_SOURCE] = "ML"

    for names, pred in zip(X_test, y_pred):
        print(names)
        print(pred)
        print()

    services.save_json("out/sub_ml.json", no_sub)


def test_grouping():
    products = services.read_json(paths.products_out)
    # products = add_filtered_names(products, remove_subcat=False)
    relevant_keys = {keys.FILTERED_NAMES, keys.SUBCAT, keys.CLEAN_NAMES, keys.BRAND}
    products = [services.filter_keys(p, relevant_keys) for p in products]

    keyfunc = lambda product: product.get(keys.BRAND, "")
    products = sorted(products, key=keyfunc)
    for key, items in itertools.groupby(products, key=keyfunc):
        print(key, items)


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)
    test_grouping()
