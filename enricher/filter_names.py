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
                s = s.replace(token, "")
            print(s, word)
    return s


def remove_color(s, clean_colors):
    for color in clean_colors:
        #  a string should include all tokens of the removal string
        if color in s and set(s.split()).issuperset(color.split()):
            s = s.replace(color, "")
            for token in color.split():
                s = s.replace(token, "")
                if token in color_dict:
                    s = s.replace(color_dict.get(token), "")

            print(s, color)
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

    colors = product.get(keys.COLOR, []) + product.get(keys.VARIANT_NAME, [])
    clean_colors = color_to_clean(colors)

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


color_original_to_clean = {}


def color_to_clean(colors):
    """
    colors = services.read_json(paths.colors)
    services.save_json(paths.clean_colors, color_original_to_clean)
    """

    stopwords = {"nocolor", "no color", "cok renkli", "renkli"}

    original_to_clean = {c: services.clean_string(c) for c in colors}
    original_to_clean = {
        k: c
        for k, c in original_to_clean.items()
        if c and not c.isdigit() and not any(sw in c for sw in stopwords)
    }
    color_original_to_clean.update(original_to_clean)
    clean_colors = list(original_to_clean.values())
    clean_colors = sorted(clean_colors, key=len, reverse=True)
    return clean_colors


def filter_all_products():
    for product in tqdm(products):
        filtered_names = filter_out_known_word_groups_from_a_name(product)
        filtered_names = Counter(filtered_names)
        product["filtered_names"] = filtered_names

    return products


if __name__ == "__main__":
    products = services.read_json(paths.products_with_brand_and_subcat)
    products_filtered = filter_all_products()
    services.save_json(paths.products_filtered, products_filtered)
