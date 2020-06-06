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


def svd():
    # model_topics(sku_name_strings_in_subcat)
    tfidf_vectorizer = TfidfVectorizer()
    tfidf_matrix = tfidf_vectorizer.fit_transform(sku_name_strings_in_subcat)
    svd = TruncatedSVD(n_components=3)
    svdMatrix = svd.fit_transform(tfidf_matrix)
    tokens = tfidf_vectorizer.get_feature_names()
    print(tfidf_matrix.shape, svdMatrix.shape)
    print(svdMatrix.components_)


def new_top_words(model, feature_names, n_top_words):
    for topic_idx, topic in enumerate(model.components_):
        # print(topic)
        sorted_topics = topic.argsort()
        # print(sorted_topics)
        # print([i for i in sorted_topics if i >0.9])
        for i in topic.argsort()[:-n_top_words - 1:-1]:
            # print(i, feature_names[i], sorted_topics[i])
            ...

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
    n_samples = 2000
    n_features = 800
    n_components = 7
    n_top_words = 1

    try:
        tf_vectorizer = CountVectorizer(max_features=n_features, ngram_range=(1, 1))
        tf_matrix = tf_vectorizer.fit_transform(sentences)
    except ValueError:
        return []

    lda = LatentDirichletAllocation(n_components=n_components, max_iter=20,
                                    learning_method='online',
                                    learning_offset=50.,
                                    random_state=0)
    lda.fit(tf_matrix)

    tf_feature_names = tf_vectorizer.get_feature_names()
    # topics = lda.transform(sentences[:3])
    # print(topics)

    return new_top_words(lda, tf_feature_names, n_top_words)



def nlp():
    lda_topics = {}
    tree = services.read_json(output_dir / "sub_tree_stripped.json")
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
        print(subcat)

        top_words = lda(sku_name_strings_in_subcat)
        print(top_words)
        print()
        lda_topics[subcat] = top_words

    remove_brands(lda_topics)


# TODO remove brands from top_words

def remove_brands(lda_topics):
    brands_in_results = services.read_json(output_dir / "brands_in_results.json")
    brands_in_results = set(brands_in_results)
    brands_in_results = brands_in_results.difference({"domates", "biber"})
    for sub, topics in lda_topics.items():
        topics = [t for t in topics if t not in brands_in_results and len(t) > 2 and not t.isdigit()]
        lda_topics[sub] = topics

    services.save_json(output_dir / "lda_topics1.json", lda_topics)


def clean_for_lda():
    """
    remove barcodes, all sizes, subcats, brands, gender, color, cat, ...
    """
    ...


nlp()
