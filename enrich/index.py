from collections import defaultdict
import services


def create_inverted_index(words):
    stopwords = {"ml", "gr", "adet", "ve", "and", "ile"}
    index = defaultdict(set)
    for word in words:
        for token in word.split():
            if token in stopwords or len(token) == 1:
                continue
            index[token].add(word)
    index = {k: list(v) for k, v in index.items()}
    return index



def create_indexes():
    clean_brands = services.read_json("cleaner/clean_brands.json")
    brand_index = create_inverted_index(clean_brands)
    services.save_json("indexes/brand_index.json", brand_index)

    clean_cats = services.read_json("cleaner/clean_cats.json")
    clean_cats.append("bebek bezi")
    cat_index = create_inverted_index(clean_cats)
    services.save_json("indexes/cat_index.json", cat_index)
