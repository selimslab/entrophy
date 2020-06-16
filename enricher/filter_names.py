from collections import Counter

import itertools

from tqdm import tqdm

from paths import output_dir
import services
import constants as keys
import paths as paths

men = {"erkek", "men", "bay", "man"}
woman = {"kadin", "women", "bayan", "woman"}
child = {"cocuk", "child", "children", "bebe"}
unisex = {"unisex"}

gender = set(itertools.chain.from_iterable([men, woman, child, unisex]))

color_pairs = [
    ("blue", "mavi"),
    ("beyaz", "white"),
    ("siyah", "black"),
    ("kirmizi", "red"),
    ("altin", "gold"),
    ("yellow", "sari"),
    ("green", "yesil"),
    ("dark", "koyu"),
]

color_dict = {}

for pair in color_pairs:
    color_dict[pair[0]] = pair[1]
    color_dict[pair[1]] = pair[0]

stopwords = {
    "ve",
    "and",
    "ile",
    "adet",
    "for",
    "icin",
    "veya",
    "li",
    "lu",
    "ml",
    "gr",
    "kg",
    "lt",
}


def remove_a_list_of_strings(s: str, to_remove: list):
    for word in to_remove:
        #  a string should include all tokens of the removal string
        if word in s and set(s.split()).issuperset(word.split()):
            s = s.replace(word, "")
            for token in word.split():
                if s and token in s:
                    s = s.replace(token, "")
    return s


def remove_color(s, clean_colors):
    for color in clean_colors:
        if color in s and set(s.split()).issuperset(color.split()):
            s = s.replace(color, "").strip()
            for token in color.split():
                if s and token in s:
                    s = s.replace(token, "").strip()
                if s and token in color_dict:
                    s = s.replace(color_dict.get(token), "")
    return s


def is_known_token(s: str):
    return services.is_barcode(s) or s in gender or s in stopwords


def filter_tokens(name: str):
    tokens = name.split()
    filtered_tokens = [t.strip() for t in tokens if not is_known_token(t)]
    filtered_tokens = [t for t in filtered_tokens if len(t) > 1 and t.isalnum()]
    return " ".join(filtered_tokens)


def filter_out_known_word_groups_from_a_name(product):
    """
    remove brand candidates, subcat_candidates, color, gender, plural_to_singular

    remove tokens like fsf343

    remove stopwords {"ve", "ile", "for", "icin", "veya", "li", "lu", "ml", "gr", "kg", "lt"}

    remove gender
        men = {"erkek", "men", "bay", "man"}
        woman = {"kadin", "women", "bayan", "woman"}
        child = {"cocuk", "child", "children", "bebe"}
        unisex = {"unisex"}

        remove len(s) > 4 and s.isdigit()

    remove non-alphanumeric chars

    remove single letters

    remove colors

    """

    # clean_colors = services.read_json(paths.clean_colors).values()

    clean_names = product.get(keys.CLEAN_NAMES, [])
    brand_candidates = product.get(keys.BRAND_CANDIDATES, [])
    subcat_candidates = product.get(keys.SUBCAT_CANDIDATES, [])
    clean_colors = product.get(keys.CLEAN_COLORS, [])

    sorted_brands = sorted(list(set(brand_candidates)), key=len, reverse=True)
    sorted_subcats = sorted(list(set(subcat_candidates)), key=len, reverse=True)

    filtered_names = []
    for name in clean_names:
        name = remove_a_list_of_strings(name, sorted_brands)
        name = remove_a_list_of_strings(name, sorted_subcats)
        name = remove_color(name, clean_colors)
        name = filter_tokens(name)
        if name:
            filtered_names.append(name)

    return filtered_names


def add_filtered_names(products):
    for product in tqdm(products):
        filtered_names = filter_out_known_word_groups_from_a_name(product)
        filtered_names = Counter(filtered_names)
        product["filtered_names"] = filtered_names

    return products


if __name__ == "__main__":
    ...