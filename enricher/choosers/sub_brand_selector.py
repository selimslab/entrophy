from collections import Counter, OrderedDict, defaultdict
import logging
from tqdm import tqdm

import services
import paths as paths
import constants as keys

from prep.filter_names import remove_a_list_of_strings


def get_sub_brand(possible_sub_brands, clean_names):
    for sub_brand in possible_sub_brands:
        for name in clean_names:
            if sub_brand in name and set(name.split()).issuperset(
                set(sub_brand.split())
            ):
                return sub_brand


def select_subbrand(products, possible_word_groups_for_sub_brand):
    for product in tqdm(products):
        brand = product.get(keys.BRAND)
        subcat = product.get(keys.SUBCAT)
        clean_names = product.get(keys.CLEAN_NAMES, [])
        possible_sub_brands = possible_word_groups_for_sub_brand.get(subcat, {}).get(
            brand, {}
        )
        sub = get_sub_brand(possible_sub_brands, clean_names)
        if sub:
            product[keys.SUB_BRAND] = sub

    return products


def get_filtered_names_tree(products_filtered: list) -> dict:
    """cat: { sub_cat : { type: {brand: {sub_brand : [products] } }"""

    filtered_names_by_subcat_brand = defaultdict(dict)
    for product in tqdm(products_filtered):
        brand, subcat = product.get(keys.BRAND), product.get(keys.SUBCAT)

        if not (brand and subcat):
            continue

        filtered_names = product.get("filtered_names")

        if not filtered_names:
            continue

        if brand not in filtered_names_by_subcat_brand[subcat]:
            filtered_names_by_subcat_brand[subcat][brand] = []

        filtered_names_by_subcat_brand[subcat][brand].append(filtered_names)

    return filtered_names_by_subcat_brand


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
            adjusted_count = freq * (1.25 ** len(tokens))
            string_counts[s] = round(adjusted_count, 2)

    return string_counts


def filter_out_incomplete_parts(counts: dict) -> dict:
    """
    if a longer string has a higher frequency than shorter building blocks, remove the shorter ones

    Example:
        if any of "a", "b", "c", "b c", or "a b" has a lower count than  "a b c", remove the one with the lower count

    """

    to_remove = set()
    for long_word in sorted(counts, key=len, reverse=True):
        long_word_tokens = set(long_word.split())
        for short_word in sorted(counts, key=len):
            if (
                counts[short_word] < counts[long_word]
                and short_word in long_word
                and long_word_tokens.issuperset(set(short_word.split()))
            ):
                to_remove.add(short_word)

    for key in to_remove:
        del counts[key]

    return counts


def count_a_single_product(names: list, brand: str):
    """ get_word_group_frequency_for_a_product """
    word_groups_counts = Counter()
    for name in names:
        substrings = services.string_to_extending_windows(name, 4)
        for i, s in enumerate(substrings):
            substrings[i] = remove_a_list_of_strings(s, [brand])

        counts = Counter(substrings)
        adjusted_frequencies = adjust_frequencies(counts)
        word_groups_counts.update(adjusted_frequencies)

    return word_groups_counts


def get_counts_by_product(filtered_names_tree):
    """ word_group_frequency_by_product """
    for subcat, brands in filtered_names_tree.items():
        for brand, filtered_name_groups in brands.items():
            filtered_names_tree[subcat][brand] = []
            for names in filtered_name_groups:
                word_groups_counts = count_a_single_product(names, brand)
                word_groups_counts = {
                    word_group.replace(brand, "").strip(): count
                    for word_group, count in word_groups_counts.items()
                }
                ##  Bir subbrandin subbrand olabilmesi için grup içindeki item'ların 50%'sinde geçmesi gerekiyor.
                word_groups_counts = {
                    word_group: count
                    for word_group, count in word_groups_counts.items()
                    if (word_group and count >= len(names) / 2)
                }

                filtered_names_tree[subcat][brand].append(word_groups_counts)

    return filtered_names_tree


def get_counts_by_brand(counts_by_product):
    """ word_group_frequency_by_brand

    in this brand, how many products have this token
    """
    counts_by_brand = defaultdict(dict)
    for subcat, brands in counts_by_product.items():
        for brand, filtered_name_groups in brands.items():
            word_groups = [list(group.keys()) for group in filtered_name_groups]
            word_groups = services.flatten(word_groups)
            counts_by_brand[subcat][brand] = Counter(word_groups)
    return counts_by_brand


def get_counts_by_subcat(counts_by_brand):
    """ get_possible_sub_brands_by_subcat

    in this subcat, how many brands have this token
    """
    counts_by_subcat = {}
    for subcat, brands in counts_by_brand.items():
        word_groups = [
            list(freq_by_brand.keys()) for brand, freq_by_brand in brands.items()
        ]
        word_groups = services.flatten(word_groups)

        counts_by_subcat[subcat] = Counter(word_groups)

    return counts_by_subcat


def get_word_group_count_by_brand(word_counts_by_product: dict) -> dict:
    # how many times the word_group seen in all of products of this brand
    """
    wg is short for word group

    word_counts_by_product = [
        { wg1: 3, wg2: 5 },
        { wg1: 3, wg3: 1 }
    ] -> brand_count = {
        wg1: 6,
        wg2: 5,
        wg3: 1
    }
    """
    brand_count = Counter()
    for word_group_counts_for_this_product in word_counts_by_product:
        brand_count.update(Counter(word_group_counts_for_this_product))
    return brand_count


def get_possible_sub_brands(counts_by_product, counts_by_brand, counts_by_subcat):
    """ get_possible_sub_brands by subcat and brand """
    ## TODO simpler
    final_count = defaultdict(dict)
    for subcat, brands in counts_by_brand.items():

        counts_in_subcat = counts_by_subcat[subcat]
        for brand, counts_in_brand in brands.items():
            if not counts_in_brand:
                continue
            word_counts_by_product = counts_by_product[subcat][brand]

            # how many times the word_group seen in all of products of this brand
            brand_count = get_word_group_count_by_brand(word_counts_by_product)

            filtered_counts = {}
            for word_group, count_in_brand in counts_in_brand.items():
                if len(word_group) < 3:
                    continue
                # a word_group should be in a single brand of this subcat only, to be a sub-brand
                in_a_single_brand = counts_in_subcat.get(word_group) < 2
                if in_a_single_brand:
                    filtered_counts[word_group] = int(brand_count.get(word_group))

            if not filtered_counts:
                continue

            filtered_counts = filter_out_incomplete_parts(filtered_counts)

            final_count[subcat][brand] = OrderedDict(
                Counter(filtered_counts).most_common()
            )
    return final_count


def create_possible_sub_brands(filtered_names_tree):
    """

    a word_group should be in at least 2 products, to be a sub-brand

    a word_group should be in a single brand of this subcat only, to be a sub-brand

    """
    logging.info("creating possible_sub_brands..")

    counts_by_product = get_counts_by_product(filtered_names_tree)
    services.save_json(paths.output_dir / "counts_by_product.json", counts_by_product)

    # in this brand, how many products have this token
    counts_by_brand = get_counts_by_brand(counts_by_product)
    services.save_json(paths.output_dir / "counts_by_brand.json", counts_by_brand)

    # in this subcat, how many brands have this token
    counts_by_subcat = get_counts_by_subcat(counts_by_brand)
    services.save_json(paths.output_dir / "counts_by_subcat.json", counts_by_subcat)

    possible_word_groups_for_sub_brand = get_possible_sub_brands(
        counts_by_product, counts_by_brand, counts_by_subcat
    )

    services.save_json(
        paths.output_dir / "possible_word_groups_for_sub_brand.json",
        possible_word_groups_for_sub_brand,
    )

    return possible_word_groups_for_sub_brand


def run():
    filtered_names_tree = services.read_json(paths.filtered_names_tree)
    create_possible_sub_brands(filtered_names_tree)


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)
    run()
