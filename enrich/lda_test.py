# Author: Olivier Grisel <olivier.grisel@ensta.org>
#         Lars Buitinck
#         Chyi-Kwei Yau <chyikwei.yau@gmail.com>
# License: BSD 3 clause

from time import time

from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.decomposition import NMF, LatentDirichletAllocation
from sklearn.decomposition import TruncatedSVD

from paths import input_dir, output_dir

import itertools
from tqdm import tqdm

import services


def print_top_words(model, feature_names, n_top_words):
    for topic_idx, topic in enumerate(model.components_):
        message = "Topic #%d: " % topic_idx
        message += " ".join([feature_names[i]
                             for i in topic.argsort()[:-n_top_words - 1:-1]])
        print(message)
    print()


# Load the 20 newsgroups dataset and vectorize it. We use a few heuristics
# to filter out useless terms early on: the posts are stripped of headers,
# footers and quoted replies, and common English words, words occurring in
# only one document or in at least 95% of the documents are removed.

print("Loading dataset...")


def model_topics(data_samples):
    # Use tf-idf features for NMF.
    print("Extracting tf-idf features for NMF...")
    tfidf_vectorizer = TfidfVectorizer()

    t0 = time()
    tfidf = tfidf_vectorizer.fit_transform(data_samples)

    # Use tf (raw term count) features for LDA.
    print("Extracting tf features for LDA...")
    tf_vectorizer = CountVectorizer(max_features=n_features)
    t0 = time()
    tf = tf_vectorizer.fit_transform(data_samples)
    print()

    # Fit the NMF model
    print("Fitting the NMF model (Frobenius norm) with tf-idf features, "
          "n_samples=%d and n_features=%d..."
          % (n_samples, n_features))
    t0 = time()
    nmf = NMF(n_components=n_components, random_state=1,
              alpha=.1, l1_ratio=.5).fit(tfidf)

    print("\nTopics in NMF model (Frobenius norm):")
    tfidf_feature_names = tfidf_vectorizer.get_feature_names()
    print_top_words(nmf, tfidf_feature_names, n_top_words)

    # Fit the NMF model
    print("Fitting the NMF model (generalized Kullback-Leibler divergence) with "
          "tf-idf features, n_samples=%d and n_features=%d..."
          % (n_samples, n_features))
    t0 = time()
    nmf = NMF(n_components=n_components, random_state=1,
              beta_loss='kullback-leibler', solver='mu', max_iter=1000, alpha=.1,
              l1_ratio=.5).fit(tfidf)

    print("\nTopics in NMF model (generalized Kullback-Leibler divergence):")
    tfidf_feature_names = tfidf_vectorizer.get_feature_names()
    print_top_words(nmf, tfidf_feature_names, n_top_words)


def new_top_words(model, feature_names, n_top_words):
    for topic_idx, topic in enumerate(model.components_):
        for i in topic.argsort()[:-n_top_words - 1:-1]:
            print(i, feature_names[i])
    top_words = (
        " ".join(
            [
                feature_names[i]
                for i in topic.argsort()[:-n_top_words - 1:-1]
            ]
        )
        for topic_idx, topic in enumerate(model.components_)
    )
    return list(set(top_words))


def lda(sentences: list):
    try:
        tf_vectorizer = CountVectorizer(max_features=n_features)
        tf_matrix = tf_vectorizer.fit_transform(sentences)
    except ValueError:
        return []

    lda = LatentDirichletAllocation(n_components=n_components, max_iter=5,
                                    learning_method='online',
                                    learning_offset=50.,
                                    random_state=0)
    lda.fit(tf_matrix)

    tf_feature_names = tf_vectorizer.get_feature_names()
    # topics = lda.transform(sentences[:3])
    # print(topics)

    return new_top_words(lda, tf_feature_names, n_top_words)


def svd():
    # model_topics(sku_name_strings_in_subcat)
    tfidf_vectorizer = TfidfVectorizer()
    tfidf_matrix = tfidf_vectorizer.fit_transform(sku_name_strings_in_subcat)
    svd = TruncatedSVD(n_components=3)
    svdMatrix = svd.fit_transform(tfidf_matrix)
    tokens = tfidf_vectorizer.get_feature_names()
    print(tfidf_matrix.shape, svdMatrix.shape)
    print(svdMatrix.components_)


def nlp():
    top_10_words_by_subcat = {}
    tree = services.read_json(output_dir / "sub_tree_stripped.json")
    for subcat, brands in tqdm(tree.items()):
        sku_name_strings_in_subcat = []
        for brand, names in brands.items():
            sku_tokens = services.tokenize_a_nested_list(names)
            sku_doc = " ".join(set(sku_tokens))
            if sku_doc:
                sku_name_strings_in_subcat.append(sku_doc)

        if not sku_name_strings_in_subcat:
            continue
        if len(sku_name_strings_in_subcat) < 2:
            continue
        print(subcat)

        top_words = lda(sku_name_strings_in_subcat)
        print(top_words)
        print()
        top_10_words_by_subcat[subcat] = top_words

    services.save_json("top_10_words_by_subcat.json", top_10_words_by_subcat)


n_samples = 2000
n_features = 1000
n_components = 7
n_top_words = 1

nlp()

# TODO remove brands from top_words
