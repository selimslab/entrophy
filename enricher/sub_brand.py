from collections import Counter, OrderedDict, defaultdict
import logging

from tqdm import tqdm

import services
import paths as paths
import constants as keys

from filter_names import add_filtered_names


def get_doc_freq(names: list):
    doc_freq = Counter()
    for name in names:
        substrings = services.get_all_contigious_substrings_of_a_string(name)
        name_freq = Counter(substrings)
        doc_freq.update(name_freq)
    return doc_freq


def get_word_group_frequency_by_product(filtered_names_tree: dict):
    """
    sliding window frequency
    """
    for subcat, brands in filtered_names_tree.items():
        for brand, name_groups in brands.items():
            freqs = []
            for group in name_groups:
                names = [[name] * count for name, count in group.items()]
                names = services.flatten(names)
                doc_freq = get_doc_freq(names)
                freqs.append(doc_freq)
            filtered_names_tree[subcat][brand] = freqs
    return filtered_names_tree


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

        # a word_group should be in a single brand of this subcat only, to be a sub-brand
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
                if (word_group in possible_sub_brands_for_this_subcat)  # and count > 1
            }

            possible_sub_brands_by_brand[subcat][brand] = OrderedDict(
                Counter(filtered_freq_by_brand).most_common()
            )
    return possible_sub_brands_by_brand


def decrease_sub_token_count(sub_brand_freqs):
    """ decrease_count_of_tokens_in_multi_token_word_groups
    """
    for subcat, brands in sub_brand_freqs.items():
        for brand, freq_by_brand in brands.items():
            for word_group, count in freq_by_brand.items():
                tokens = word_group.split()
                if len(tokens) == 1:
                    continue
                for token in tokens:
                    if token in freq_by_brand:
                        freq_by_brand[token] -= 1

    return sub_brand_freqs


def pre_test_decrease_sub_token_count():
    case = {"x": {"y": {"a": 2, "b": 3, "a b": 1}}}
    res = decrease_sub_token_count(case)

    assert res == {"x": {"y": {"a": 1, "b": 2, "a b": 1}}}


def create_possible_sub_brands(filtered_names_tree):
    word_group_frequency_by_product = get_word_group_frequency_by_product(
        filtered_names_tree
    )
    possible_sub_brands_by_brand = get_possible_sub_brands_by_brand(
        word_group_frequency_by_product
    )
    possible_sub_brands_by_subcat = get_possible_sub_brands_by_subcat(
        possible_sub_brands_by_brand
    )
    possible_sub_brands_by_brand = filter_possible_sub_brands(
        possible_sub_brands_by_brand, possible_sub_brands_by_subcat
    )

    # OrderedDict(filtered_freq_by_brand.most_common())
    services.save_json(
        paths.output_dir / "word_group_frequency_by_product.json",
        word_group_frequency_by_product,
    )

    services.save_json(
        paths.output_dir / "possible_sub_brands_by_brand.json", possible_sub_brands_by_brand
    )


def create_filtered_names_tree_by_subcat_and_brand(products_filtered):
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


def filter():
    products_with_brand_and_subcat = services.read_json(
        paths.products_with_brand_and_subcat
    )
    products_filtered = add_filtered_names(products_with_brand_and_subcat)
    services.save_json(paths.products_filtered, products_filtered)


def count():
    products_filtered = services.read_json(paths.products_filtered)
    filtered_names_tree = create_filtered_names_tree_by_subcat_and_brand(products_filtered)
    services.save_json(paths.filtered_names_tree, filtered_names_tree)
    logging.info("creating possible_sub_brands..")
    create_possible_sub_brands(filtered_names_tree)


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)
    # filter()
    count()
