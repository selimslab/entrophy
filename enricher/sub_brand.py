from collections import Counter, OrderedDict, defaultdict
import logging

from tqdm import tqdm

import services
import paths as paths
import constants as keys

from filter_names import add_filtered_names


def sliding_window_frequency(s: list):
    substrings = services.get_all_contigious_substrings_of_a_string(s)
    return Counter(substrings)


def adjust_frequencies(string_counts: Counter):
    """
    Carte Dor gibi iki kelimeli subbrand'lerde
    Carte kelimesi Carte Dor'dan daha fazla gelebilir.

    Bundan dolayı iki kelimeli tekrar eden token'lara öncelik verebilmek
    için frekanslarını 1.25 ile çarpalım
    80% ihtimal geçmiş olmasını yeterli görmüş oluyoruz

    3 kelimelileri de 1.25X1.25=1.56 ile çarpalım.
    """

    for s, freq in string_counts.items():
        tokens = s.split()
        if len(tokens) > 1:
            try:
                string_counts[s] = int(freq) * (1.25 ** len(tokens))
            except TypeError as e:
                logging.error(e)
                print(string_counts)
    return string_counts


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
                if (word_group in possible_sub_brands_for_this_subcat and count > 1)
            }

            possible_sub_brands_by_brand[subcat][brand] = OrderedDict(
                Counter(filtered_freq_by_brand).most_common()
            )
    return possible_sub_brands_by_brand


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

        window_counts = Counter()
        for name in filtered_names:
            counts = sliding_window_frequency(name)
            adjusted_frequencies = adjust_frequencies(counts)
            window_counts.update(adjusted_frequencies)

        tree[subcat][brand].append(window_counts)

    return tree


def filter():
    products_with_brand_and_subcat = services.read_json(
        paths.products_with_brand_and_subcat
    )
    products_filtered = add_filtered_names(products_with_brand_and_subcat)
    services.save_json(paths.products_filtered, products_filtered)


def create_possible_sub_brands():
    products_filtered = services.read_json(paths.products_filtered)
    filtered_names_tree = create_filtered_names_tree_by_subcat_and_brand(products_filtered)
    services.save_json(paths.filtered_names_tree, filtered_names_tree)

    logging.info("creating possible_sub_brands..")

    possible_sub_brands_by_brand = get_possible_sub_brands_by_brand(
        filtered_names_tree
    )
    possible_sub_brands_by_subcat = get_possible_sub_brands_by_subcat(
        possible_sub_brands_by_brand
    )
    possible_sub_brands_by_brand = filter_possible_sub_brands(
        possible_sub_brands_by_brand, possible_sub_brands_by_subcat
    )

    services.save_json(
        paths.output_dir / "possible_sub_brands_by_brand.json", possible_sub_brands_by_brand
    )


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)
    filter()
    create_possible_sub_brands()
