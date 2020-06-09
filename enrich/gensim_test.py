from collections import defaultdict
from gensim import corpora, models
import logging

logging.basicConfig(
    format="%(asctime)s : %(levelname)s : %(message)s", level=logging.INFO
)

docs = [
    "Human machine interface for lab abc computer applications",
    "A survey of user opinion of computer system response time",
    "The EPS user interface management system",
    "System and human system engineering testing of EPS",
    "Relation of user perceived response time to error measurement",
    "The generation of random binary unordered trees",
    "The intersection graph of paths in trees",
    "Graph minors IV Widths of trees and well quasi ordering",
    "Graph minors A survey",
]

documents = [""]
# remove common words and tokenize
stoplist = set("for a of the and to in".split())
texts = [
    [word for word in document.lower().split() if word not in stoplist]
    for document in documents
]

# remove words that appear only once
frequency = defaultdict(int)
for text in texts:
    for token in text:
        frequency[token] += 1

texts = [[token for token in text if frequency[token] > 1] for text in texts]

dictionary = corpora.Dictionary(texts)
corpus = [dictionary.doc2bow(text) for text in texts]

tfidf = models.TfidfModel(corpus)  # step 1 -- initialize a model
corpus_tfidf = tfidf[corpus]

lsi_model = models.LsiModel(
    corpus_tfidf, id2word=dictionary, num_topics=2
)  # initialize an LSI transformation
corpus_lsi = lsi_model[corpus_tfidf]

lsi_model.print_topics(2)

for doc, as_text in zip(corpus_lsi, documents):
    print(doc, as_text)
