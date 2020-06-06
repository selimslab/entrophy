from collections import OrderedDict, Counter, defaultdict
from operator import itemgetter
import itertools
from pprint import pprint
from tqdm import tqdm
import re

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import pandas as pd

from paths import input_dir, output_dir
import services
from services.size_finder import size_finder
import constants as keys



def go():
    tree = services.read_json(output_dir / "sub_tree.json")

    pprint(sorted(list(tree.keys())))


def sub_freq():
    """ freq of tokens by subcat and by brand

    if some tokens are together in a given sku, one of these tokens cannot be a type
    """

    tree = services.read_json(output_dir / "sub_tree_stripped.json")

    subcat_freqs = {}
    brand_freqs = defaultdict(dict)

    togethers = defaultdict(dict)

    for subcat, brands in tqdm(tree.items()):
        tokens_for_this_subcat = []
        brands_of_a_token = defaultdict(set)
        for brand, stripped_groups in brands.items():
            tokens_for_this_brand = []
            for name_group in stripped_groups:
                tokens_for_this_sku = itertools.chain.from_iterable(name.split() for name in name_group)
                # dedup tokens for sku
                tokens = [t for t in set(tokens_for_this_sku) if len(t) > 2]
                tokens = list(set(tokens))

                tokens_for_this_brand += tokens

            tokens_for_this_brand = services.flatten(tokens_for_this_brand)
            tokens_for_this_subcat += tokens_for_this_brand
            for token in tokens_for_this_brand:
                brands_of_a_token[token].add(brand)

            token_freq_for_this_brand = OrderedDict(Counter(tokens_for_this_brand).most_common())
            token_freq_for_this_brand = {k: v for k, v in token_freq_for_this_brand.items() if v > 1}
            brand_freqs[subcat][brand] = token_freq_for_this_brand

        # include a token only if it is in multiple brands of a subcat
        #
        tokens_for_this_subcat = [t for t in tokens_for_this_subcat if len(brands_of_a_token.get(t, [])) > 1]
        subcat_freq = OrderedDict(Counter(tokens_for_this_subcat).most_common(10))
        subcat_freq = {k: v for k, v in subcat_freq.items() if v > 3}
        subcat_freqs[subcat] = subcat_freq

    services.save_json(output_dir / "top_10_tokens_for_every_subcat.json", subcat_freqs)
    services.save_json(output_dir / "brand_freqs.json", brand_freqs)
    services.save_json(output_dir / "togethers.json", togethers)


def cluster():
    tree = services.read_json(output_dir / "sub_tree_stripped.json")
    for subcat, brands in tqdm(tree.items()):
        docs = itertools.chain.from_iterable(brands.values())
        sku_name_strings_in_subcat = [" ".join(tokens) for tokens in docs]
        sku_name_strings_in_subcat = [s for s in sku_name_strings_in_subcat if s]
        if not sku_name_strings_in_subcat:
            continue

        tfidf_vectorizer = TfidfVectorizer()
        tfidf_matrix = tfidf_vectorizer.fit_transform(sku_name_strings_in_subcat)
        tokens = tfidf_vectorizer.get_feature_names()

        d = {}
        for row in tfidf_matrix.toarray():
            for name, tfidf in zip(tokens, row):
                d[name] = tfidf

        print(subcat)
        sel = services.get_most_frequent_key(d)
        print(sel, round(d[sel], 2))
        print("\n")
        """
        df = pd.DataFrame(tfidf_matrix.toarray(), columns=tfidf_vectorizer.get_feature_names())
        print(df)
        
        kmeans = KMeans(n_clusters=2).fit(tfidf_matrix)
        tfidfs = tfidf_vectorizer.transform(sku_name_strings_in_subcat)
        # predictions = kmeans.predict(tfidfs)

        """


def test_vectorizer():
    corpus = """
    Simple example with Cats and Mouse
    Another simple example with dogs and cats
    Another simple example with mouse and cheese
    """.split("\n")[1:-1]
    tfidf_vectorizer = TfidfVectorizer()
    tfidf_matrix = tfidf_vectorizer.fit_transform(corpus)
    tokens = tfidf_vectorizer.get_feature_names()
    # df = pd.DataFrame(tfidf_matrix.toarray(), columns=tokens)
    # print(df)
    print(tokens)
    for row in tfidf_matrix.toarray():
        d = {}
        for name, tfidf in zip(tokens, row):
            d[name] = tfidf

        print(services.get_most_frequent_key(d))
        print("---")


if __name__ == "__main__":
    # create_sub_tree()
    sub_freq()

    """
    
    salca
        domates 
            - oncu 
            - tat
            - tamek 
        biber 
            - oncu 
            - tat
            - xyz 
    
    """
