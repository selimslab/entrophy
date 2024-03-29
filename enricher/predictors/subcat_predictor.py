import logging
import itertools

from tqdm import tqdm

import services
import constants as keys
import paths as paths

from prep.filter_names import add_filtered_names
from prep.indexer import create_indexes

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB


def split_training_and_test(products):
    if not products:
        return []

    with_sub = [
        p
        for p in products
        if keys.SUBCAT in p  # and p.get(keys.SUBCAT_SOURCE) != "global_name"
    ]
    no_sub = [
        p
        for p in products
        if keys.SUBCAT not in p  # or p.get(keys.SUBCAT_SOURCE) == "global_name"
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

    return X_train, y_train, X_test, no_sub


def subcat_prediction_generator(X_train, y_train, X_test, no_sub):
    """
    use products with subcat as training, and classify the remaining
    """
    if not X_train or not y_train or not X_test:
        return

    """
    tf-idf is also possible 

    tfidf_transformer = TfidfTransformer()
    X_train_tfidf = tfidf_transformer.fit_transform(X_train_counts)
    """
    count_vect = CountVectorizer()
    try:
        X_train_counts = count_vect.fit_transform(X_train)
    except ValueError:
        return

    clf = MultinomialNB().fit(X_train_counts, y_train)

    test_vector = count_vect.transform(X_test)
    y_pred = clf.predict(test_vector)
    log_probas = clf.predict_log_proba(test_vector)

    for i, product in enumerate(no_sub):
        predicted_class = y_pred[i]
        idx = y_train.index(predicted_class)

        # might be used for a probability threshold
        try:
            log_prob = log_probas[i][idx]
        except IndexError:
            continue

        the_id = product.get(keys.PRODUCT_ID)
        if not the_id:
            the_id = product.get(keys.SKU_ID)

        yield the_id, predicted_class


def group_by_brand(products):
    keyfunc = lambda product: product.get(keys.BRAND, "")
    products = sorted(products, key=keyfunc)
    for key, items in itertools.groupby(products, key=keyfunc):
        yield key, items


def get_subcat_predictions(products: list):
    *rest, possible_subcats_by_brand = create_indexes(products)

    # keep subcats for ML, remove brand and others
    products = add_filtered_names(
        products, possible_subcats_by_brand, remove_subcat=False
    )

    # for brand, products in group_by_brand(products):
    X_train, y_train, X_test, no_sub = split_training_and_test(products)
    predicted = subcat_prediction_generator(X_train, y_train, X_test, no_sub)
    return {the_id: prediction for the_id, prediction in predicted}


def simple_bayes_example():
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
    products = services.read_json(paths.products_out)
    get_subcat_predictions(products)
