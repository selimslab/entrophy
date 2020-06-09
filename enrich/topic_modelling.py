from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation


def new_top_words(model, feature_names, n_top_words):
    top_words = (
        " ".join([feature_names[i] for i in topic.argsort()[: -n_top_words - 1: -1]])
        for topic_idx, topic in enumerate(model.components_)
    )
    return list(set(top_words))


def lda(sentences: list, n_gram=2, n_top_words=1):
    n_features = 800
    n_components = 7  # number of topics

    try:
        tf_vectorizer = CountVectorizer(
            max_features=n_features, ngram_range=(1, n_gram)
        )
        tf_matrix = tf_vectorizer.fit_transform(sentences)
    except ValueError:
        return []

    lda = LatentDirichletAllocation(
        n_components=n_components, learning_method="online", random_state=0,
    )
    lda.fit(tf_matrix)

    tf_feature_names = tf_vectorizer.get_feature_names()

    # topics = lda.transform(tf_matrix)
    # topics = lda.transform(sentences[:3])
    # print(topics)

    return new_top_words(lda, tf_feature_names, n_top_words)
