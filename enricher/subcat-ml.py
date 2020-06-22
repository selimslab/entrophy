import logging
from typing import List

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
    relevaant_keys = {keys.FILTERED_NAMES, keys.SUBCAT}
    products = [services.filter_keys(p, relevaant_keys) for p in products]
    with_sub = [p for p in products if keys.SUBCAT in p]
    no_sub = [p for p in products if keys.SUBCAT not in p]

    X_train = []
    y_train = []
    logging.info("creating training..")
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

    for product in tqdm(no_sub):
        names = product.get(keys.FILTERED_NAMES, [])
        pred = clf.predict(count_vect.transform([" ".join(names)]))
        print(names)
        print(pred)
        print()


if __name__ == "__main__":
    classify_subcat()
