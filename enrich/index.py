from collections import defaultdict, Counter
import services
from paths import *
from tqdm import tqdm


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


def create_brand_index():
    brands = services.read_json("cleaner/joined_brands.json")
    brands = brands.get("brands")
    clean_brands = services.list_to_clean_set(brands)
    services.save_json(clean_brands_path, clean_brands)

    brand_index = create_inverted_index(clean_brands)
    services.save_json(brand_index_path, brand_index)

    # but they are sets already, freq=1 ?
    brand_freq = Counter([t for brand in clean_brands for t in brand.split()])
    services.save_json(temp / "brand_freq.json", brand_freq)


def create_cat_index():
    cats = services.read_json("cleaner/joined_categories.json")
    cats = cats.get("categories")
    clean_cats = services.list_to_clean_set(cats)
    services.save_json(clean_cats_path, clean_cats)

    clean_cats.append("bebek bezi")
    cat_index = create_inverted_index(clean_cats)
    services.save_json(cat_index_path, cat_index)

    cat_freq = Counter([t for cat in clean_cats for t in cat.split()])
    services.save_json(temp / "cat_freq.json", cat_freq)


def all_name_freq():
    """ freq of tokens in all names """
    guess_docs = services.read_json(guess_docs_path)
    names = [doc.get("clean_names") for doc in guess_docs]
    names = services.collections_util.flatten(names)
    name_freq = Counter([word for name in names if name for word in name.split()])
    services.save_json("freq/name_freq.json", name_freq)


if __name__ == "__main__":
    ...
