from collections import Counter

import itertools

from tqdm import tqdm

from paths import output_dir
import services
import constants as keys

men = {"erkek", "men", "bay", "man"}
woman = {"kadin", "women", "bayan", "woman"}
child = {"cocuk", "child", "children", "bebe"}
unisex = {"unisex"}

gender = set(itertools.chain.from_iterable([men, woman, child, unisex]))

color = {
    "mavi",
    "blue",
    "beyaz",
    "white",
    "siyah",
    "black",
    "kirmizi",
    "red",
    "altin",
    "gold",
    "yellow",
    "sari",
    "green",
    "yesil",
}

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
    for bad in to_remove:
        #  a string should include all tokens of the removal string
        if bad in s and set(s.split()).issuperset(bad.split()):
            s = s.replace(bad, "")
    return s


def is_known_token(s: str):
    return (
            services.is_barcode(s)
            or s in gender
            or s in color
            or s in stopwords
    )


def filter_tokens(name: str):
    tokens = name.split()
    filtered_tokens = [t.strip() for t in tokens if not is_known_token(t)]
    filtered_tokens = [services.plural_to_singular(t) for t in filtered_tokens]
    filtered_tokens = [t for t in filtered_tokens if len(t) > 1 and t.isalnum()]
    return " ".join(filtered_tokens)


def filter_out_knownword_groups_from_a_name(product, clean_colors):
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
    clean_names = product.get(keys.CLEAN_NAMES)
    brand_candidates = product.get(keys.BRAND_CANDIDATES)
    subcat_candidates = product.get(keys.SUBCAT_CANDIDATES)

    sorted_brands = sorted(brand_candidates.keys(), key=len, reverse=True)
    sorted_subcats = sorted(subcat_candidates.keys(), key=len, reverse=True)

    filtered_names = []
    for name in clean_names:
        name = remove_a_list_of_strings(name, sorted_brands)
        name = remove_a_list_of_strings(name, sorted_subcats)
        name = remove_a_list_of_strings(name, clean_colors)
        name = filter_tokens(name)
        if name:
            filtered_names.append(name)

    return filtered_names


def filter_all_products():
    products = services.read_json(output_dir / "products_with_brand_and_sub_cat.json")

    clean_colors = services.read_json(output_dir / "clean_colors.json")
    clean_colors = sorted(list(clean_colors), key=len, reverse=True)

    for product in tqdm(products):
        filtered_names = filter_out_knownword_groups_from_a_name(product, clean_colors)
        filtered_names = Counter(filtered_names)
        print(filtered_names)
        product["filtered_names"] = filtered_names

    services.save_json(output_dir / "products_filtered.json", products)


if __name__ == "__main__":
    filter_all_products()
