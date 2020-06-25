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
        if keys.SUBCAT in p # and p.get(keys.SUBCAT_SOURCE) != "global_name"
    ]
    no_sub = [
        p
        for p in products
        if keys.SUBCAT not in p # or p.get(keys.SUBCAT_SOURCE) == "global_name"
    ]

    X_train = []
    y_train = []
    logging.info("training..")
    for product in tqdm(with_sub):
        filtered_names = product.get(keys.FILTERED_NAMES, [])
        sub = product.get(keys.SUBCAT)
        X_train += filtered_names
        y_train += [sub] * len(filtered_names)

    filtered_names = [product.get(keys.FILTERED_NAMES, []) for product in tqdm(no_sub)]
    X_test = [" ".join(names) for names in filtered_names]

    if not X_train or not y_train or not X_test:
        return []

    count_vect = CountVectorizer()
    try:
        X_train_counts = count_vect.fit_transform(X_train)
    except ValueError:
        return []
    # tfidf_transformer = TfidfTransformer()
    # X_train_tfidf = tfidf_transformer.fit_transform(X_train_counts)
    clf = MultinomialNB().fit(X_train_counts, y_train)

    test_vector = count_vect.transform(X_test)
    y_pred = clf.predict(test_vector)
    log_probas = clf.predict_log_proba(test_vector)

    for i, product in enumerate(no_sub):
        predicted_class = y_pred[i]
        idx = y_train.index(predicted_class)
        try:
            log_prob = log_probas[i][idx]
            print(X_test[i])
            print(predicted_class, log_prob, max(log_probas[i]), sum(log_probas[i]))
            if log_prob < -100:
                continue
            print()
        except IndexError:
            continue
        product[keys.SUBCAT] = predicted_class
        product[keys.SUBCAT_SOURCE] = "ML"

    return no_sub


def group_by_brand(products):
    keyfunc = lambda product: product.get(keys.BRAND, "")
    products = sorted(products, key=keyfunc)
    for key, items in itertools.groupby(products, key=keyfunc):
        yield key, items


def run():
    products = services.read_json(paths.products_out)
    *rest, possible_subcats_by_brand = get_indexes(products)

    # keep subcats for ML, remove brand and others
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
    # for brand, products in group_by_brand(products):
    predicted = predict_subcat(list(products))
    subcat_predicted += predicted

    services.save_json("stage/ML_subcat_predicted.json", subcat_predicted)


def test_mnb():
    import numpy as np

    rng = np.random.RandomState(1)
    X = rng.randint(5, size=(6, 100))
    y = np.array([1, 2, 3, 4, 5, 6])
    from sklearn.naive_bayes import MultinomialNB

    clf = MultinomialNB()
    clf.fit(X, y)

    test = X[2:3]
    print(test)
    print(clf.predict(test))
    print(clf.predict_proba(test))


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)
    run()
