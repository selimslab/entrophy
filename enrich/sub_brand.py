from collections import Counter, OrderedDict, defaultdict
import logging

from tqdm import tqdm

import services
from paths import output_dir
import constants as keys


def get_all_contigious_substrings_of_a_string(s: str):
    tokens = s.split()
    n = len(tokens)
    substrings = []
    for start in range(n):
        for end in range(1, n + 1):
            word_group = " ".join(tokens[start:end])
            substrings.append(word_group)
    return substrings


def get_name_freq(s: str):
    substrings = get_all_contigious_substrings_of_a_string(s)
    return Counter(substrings)


def get_doc_freq(names: list):
    doc_freq = Counter()
    for name in names:
        name_freq = get_name_freq(name)
        doc_freq.update(name_freq)
    return doc_freq


def get_word_group_frequency_by_product(sub_brand_tree):
    for subcat, brands in sub_brand_tree.items():
        for brand, name_groups in brands.items():
            freqs = []
            for group in name_groups:
                names = [[name] * count for name, count in group.items()]
                names = services.flatten(names)
                doc_freq = get_doc_freq(names)
                del doc_freq[""]
                freqs.append(doc_freq)
            sub_brand_tree[subcat][brand] = freqs
    return sub_brand_tree


def get_possible_sub_brands_by_brand(doc_freq_tree):
    possible_sub_brands_by_brand = defaultdict(dict)
    for subcat, brands in doc_freq_tree.items():
        for brand, groups in brands.items():
            word_groups = [list(group.keys()) for group in groups]
            word_groups = services.flatten(word_groups)
            freq_by_brand = Counter(word_groups)
            possible_sub_brands_by_brand[subcat][brand] = freq_by_brand
    return possible_sub_brands_by_brand


def get_possible_sub_brands_by_subcat(possible_sub_brands_by_brand):
    possible_sub_brands_by_subcat = {}
    for subcat, brands in possible_sub_brands_by_brand.items():
        word_groups = [
            list(freq_by_brand.keys()) for brand, freq_by_brand in brands.items()
        ]
        word_groups = services.flatten(word_groups)
        freq_by_subcat = Counter(word_groups)

        # a word_group should be in a single brand only, to be a sub-brand
        possible_sub_brands_for_this_subcat = (
            word_group for word_group, count in freq_by_subcat.items() if count == 1
        )
        possible_sub_brands_by_subcat[subcat] = list(
            set(possible_sub_brands_for_this_subcat)
        )

    return possible_sub_brands_by_subcat


def filter_possible_sub_brands(
        possible_sub_brands_by_brand, possible_sub_brands_by_subcat
):
    for subcat, brands in possible_sub_brands_by_brand.items():
        possible_sub_brands_for_this_subcat = possible_sub_brands_by_subcat[subcat]

        for brand, freq_by_brand in brands.items():
            # a word_group should be in at least 2 products, to be a sub-brand
            filtered_freq_by_brand = {
                word_group: count
                for word_group, count in freq_by_brand.items()
                if (word_group in possible_sub_brands_for_this_subcat and count > 1)
            }

            possible_sub_brands_by_brand[subcat][brand] = OrderedDict(
                Counter(filtered_freq_by_brand).most_common()
            )
    return possible_sub_brands_by_brand


def create_possible_sub_brands(sub_brand_tree):
    word_group_frequency_by_product = get_word_group_frequency_by_product(
        sub_brand_tree
    )
    unfiltered_possible_sub_brands_by_brand = get_possible_sub_brands_by_brand(
        word_group_frequency_by_product
    )
    possible_sub_brands_by_subcat = get_possible_sub_brands_by_subcat(
        unfiltered_possible_sub_brands_by_brand
    )
    possible_sub_brands_by_brand = filter_possible_sub_brands(
        unfiltered_possible_sub_brands_by_brand, possible_sub_brands_by_subcat
    )

    # OrderedDict(filtered_freq_by_brand.most_common())
    services.save_json(
        output_dir / "word_group_frequency_by_product.json",
        word_group_frequency_by_product,
    )
    services.save_json(
        output_dir / "possible_sub_brands_by_brand.json", possible_sub_brands_by_brand
    )
    services.save_json(
        output_dir / "possible_sub_brands_by_subcat.json", possible_sub_brands_by_subcat
    )


def create_sub_brand_tree(products_filtered):
    """cat: { sub_cat : { type: {brand: {sub_brand : [products] } }"""

    tree = {}
    logging.info("create_sub_brand_tree..")

    for product in tqdm(products_filtered):
        brand, subcat = product.get(keys.BRAND), product.get(keys.SUBCAT)

        if not (brand and subcat):
            continue

        filtered_names = product.get("filtered_names")
        if not filtered_names:
            continue

        if subcat not in tree:
            tree[subcat] = {}
        if brand not in tree[subcat]:
            tree[subcat][brand] = []

        tree[subcat][brand].append(filtered_names)

    return tree


def save_sub_tree():
    products = services.read_json(output_dir / "products_filtered.json", )
    sub_brand_tree = create_sub_brand_tree(products)
    services.save_json(output_dir / "sub_brand_tree.json", sub_brand_tree)
    create_possible_sub_brands(sub_brand_tree)


if __name__ == "__main__":
    save_sub_tree()
