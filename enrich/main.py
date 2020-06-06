import multiprocessing
import os
from collections import defaultdict, Counter, OrderedDict
from tqdm import tqdm
import logging
from typing import List, Iterable, Dict
import itertools

import services
import constants as keys
from paths import input_dir, output_dir

from mongo_service import get_raw_docs_with_markets_and_cats_only


def index_brands_and_subcats() -> tuple:
    """
        "finish": [
        "kirec onleyici",
        "bulasik yikama urunleri",
        ...
        ]

    """
    brand_subcats_pairs = defaultdict(set)
    clean_brand_original_brand_pairs = {}
    sub_cat_market_pairs = defaultdict(set)

    def update_brand_subcats_pairs(brands: Iterable, subcats: Iterable, market):
        brands = list(set(brands))
        subcats = list(set(subcats))

        clean_to_original = {services.clean_name(b): b for b in brands}
        clean_brand_original_brand_pairs.update(clean_to_original)
        clean_brands = set(b for b in clean_to_original.keys() if len(b) > 1)

        clean_subcats = services.clean_list_of_strings(subcats)
        clean_subcats = [sub for sub in clean_subcats if sub]

        for sub in clean_subcats:
            sub_cat_market_pairs[sub].add(market)

        for b in clean_brands:
            brand_subcats_pairs[b].update(clean_subcats)

    def add_ty():
        ty_raw = services.read_json(input_dir / "ty_raw.json")
        for main_cat, filters in ty_raw.items():
            brands: list = filters.get("brand")
            subcats: list = filters.get("category")
            update_brand_subcats_pairs(brands, subcats, keys.TRENDYOL)

    def add_watsons():
        watsons_raw = services.read_json(input_dir / "watsons_raw.json")
        for main_cat, filters in watsons_raw.items():
            brands = filters.get("marka")
            subcats = filters.get("cats")

            update_brand_subcats_pairs(brands, subcats, keys.WATSONS)

    def add_from_raw_docs():
        raw_docs_path = input_dir / "raw_docs.json"
        if not os.path.exists(raw_docs_path):
            cursor = get_raw_docs_with_markets_and_cats_only()
            raw_docs = list(cursor)
            services.save_json(raw_docs_path, raw_docs)
        else:
            raw_docs = services.read_json(raw_docs_path)

        for doc in raw_docs:
            brand = doc.get(keys.BRAND)
            cats = doc.get(keys.CATEGORIES, [])
            market = doc.get(keys.MARKET)

            brands = [brand]
            subcats = clean_sub_cats(cats)
            update_brand_subcats_pairs(brands, subcats, market)

    logging.info("creating brand_subcats_pairs..")
    add_from_raw_docs()

    return brand_subcats_pairs, clean_brand_original_brand_pairs, sub_cat_market_pairs


def clean_brands(brands: list) -> list:
    """
     johnson s baby -> johnsons baby
    """
    return services.clean_list_of_strings(services.flatten(brands))


def add_clean_brand(sku: dict) -> dict:
    sku[keys.CLEAN_BRANDS] = clean_brands(sku.get("brands", []))
    return sku


def clean_cats(cats: list) -> list:
    return services.clean_list_of_strings(services.flatten(cats))


def add_clean_cats(sku: dict) -> dict:
    cats = sku.get(keys.CATEGORIES, [])
    sku[keys.CLEAN_CATS] = clean_cats(cats)
    return sku


def clean_sub_cats(cats: list) -> list:
    """
    her market için ayrı
    "okul kırtasiye, aksesuarları/kırtasiye/ev, pet" -> migros

    "bebek bezi/bebek, oyuncak" -> bebek bezi
    """

    subcats = []
    for cat in cats:
        if isinstance(cat, list):
            subcats.append(cat[-1])
        else:
            subcats.append(cat)

    # "bebek bezi/bebek, oyuncak" -> bebek bezi
    subcats = [sub.split("/")[0] for sub in subcats]

    # subcats = [sub.split(",")[-1] for sub in subcats]

    clean_subcats = services.clean_list_of_strings(services.flatten(subcats))
    return clean_subcats


def add_clean_subcats(sku: dict) -> dict:
    cats = sku.get(keys.CATEGORIES, [])
    sku[keys.CLEAN_SUBCATS] = clean_sub_cats(cats)
    return sku


def get_clean_skus(skus: List[dict]):
    relevant_keys = {keys.CATEGORIES, keys.BRANDS_MULTIPLE, keys.CLEAN_NAMES, keys.NAME}
    skus = [services.filter_keys(doc, relevant_keys) for doc in skus]

    with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
        skus = pool.map(add_clean_brand, tqdm(skus))
        skus = pool.map(add_clean_cats, tqdm(skus))
        skus = pool.map(add_clean_subcats, tqdm(skus))

    return skus


def get_token_lists(names: list) -> List[list]:
    names = services.flatten(names)
    names = [n for n in names if n]
    name_tokens = [name.split() for name in names]
    return name_tokens


def select_brand(brand_candidates: list) -> str:
    # TODO beware position
    if brand_candidates:
        brand_candidates = list(set(brand_candidates))
        brand = sorted(brand_candidates, key=len)[-1]
        return brand


def get_brand_candidates(sku: dict, brand_pool: set) -> list:
    """
    find brand first,
    there only a few possible cats for this brand
    indexes should reflect that too

    johnson s baby -> johnsons baby
    """
    candidates = []
    candidates += sku.get(keys.CLEAN_BRANDS, [])

    clean_names = sku.get(keys.CLEAN_NAMES, [])

    # this search is 2 parts to make it faster,
    # we don't have to search every possible brand in name
    for name in clean_names:
        # search single-word brands
        # brand is in first two tokens mostly

        name_tokens = name.split()
        start_strings = [" ".join(name_tokens[:i]) for i in range(1, 5)]
        # search multiple-word brands
        brands_from_frequent_words = [s for s in start_strings if s in brand_pool]
        candidates += brands_from_frequent_words

    return candidates


def get_frequencies_for_all_start_combinations(names: List[list]) -> dict:
    token_lists = get_token_lists(names)
    groups = []
    for token_list in tqdm(token_lists):
        for i in range(1, len(token_list) + 1):
            groups.append(" ".join(token_list[0:i]))
    groups = [s for s in groups if len(s) > 2]
    freq = OrderedDict(Counter(groups).most_common())
    return freq


def find_out_freq_cut_points(freq):
    for name, count in freq.items():
        ...


def get_frequent_start_strings_as_brands(names: List[list]) -> set:
    freq = get_frequencies_for_all_start_combinations(names)
    filtered_freq = {s: freq for s, freq in freq.items() if freq > 60}
    services.save_json(
        output_dir / "most_frequent_start_strings.json",
        OrderedDict(sorted(filtered_freq.items())),
    )

    max_brand_size = 2
    most_frequent_start_strings = set(filtered_freq.keys())
    most_frequent_start_strings = {
        b for b in most_frequent_start_strings if len(b.split()) <= max_brand_size
    }

    return most_frequent_start_strings


def add_brand_to_skus(clean_skus: List[dict], brand_subcats_pairs: dict) -> List[dict]:
    """
    0. cat and subcat are different things, beware
    1. clean well
    2. using ty_raw, wat_raw, and full skus  ->
    create
    brand : [possible cats]
    cat : [possible brands]

    so given a brand, the possible cats will be known
    """

    # brands given by vendors
    brands = brand_subcats_pairs.keys()
    brand_pool = set(brands)

    names = [sku.get(keys.CLEAN_NAMES, []) for sku in clean_skus]
    most_frequent_start_strings = get_frequent_start_strings_as_brands(names)
    brand_pool.update(most_frequent_start_strings)

    services.save_json(output_dir / "brand_pool.json", sorted(list(brand_pool)))

    bad_words = {"brn ", "markasiz", "erkek", "kadin"}

    for sku in tqdm(clean_skus):
        brand_candidates = get_brand_candidates(sku, brand_pool)
        brand_candidates = [
            b
            for b in brand_candidates
            if len(b) > 2 and not any(bad in b for bad in bad_words)
        ]

        sku[keys.BRAND_CANDIDATES] = brand_candidates
        sku[keys.BRAND] = select_brand(brand_candidates)

    return clean_skus


def get_sku_summary(skus_with_brand_and_sub_cat: List[dict]) -> List[dict]:
    summary_keys = {keys.CLEAN_NAMES, keys.BRAND, keys.SUBCAT}
    summary = [
        services.filter_keys(doc, summary_keys) for doc in skus_with_brand_and_sub_cat
    ]
    for doc in summary:
        doc["names"] = list(set(doc.pop(keys.CLEAN_NAMES)))[:3]

    summary = [services.remove_null_dict_values(doc) for doc in summary]
    return summary


def select_subcat(
        sub_cat_candidates: list, sub_cat_market_pairs: Dict[str, list],
):
    if sub_cat_candidates:
        # prioritize markets
        priority_markets = [keys.TRENDYOL, keys.GRATIS, keys.WATSONS, keys.MIGROS]
        sorted_by_length = sorted(sub_cat_candidates, key=len, reverse=True)
        for sub in sorted_by_length:
            markets_for_this_sub = sub_cat_market_pairs.get(sub, [])
            if markets_for_this_sub and any(
                    m in priority_markets for m in markets_for_this_sub
            ):
                return sub

        #  as a last resort, select longest
        sub_cat = sorted_by_length[0]
        return sub_cat


def add_sub_cat_to_skus(
        skus: List[dict],
        brand_subcats_pairs: Dict[str, list],
        sub_cat_market_pairs: Dict[str, list],
) -> List[dict]:
    """
    There are a set of possible subcats for a given brand
    we check them if any of them is in any of the names of the given sku
    this leaves us with a few candidates
    then we choose prioritizing by market
    """
    for sku in tqdm(skus):
        sub_cat_candidates = []

        clean_names = sku.get(keys.CLEAN_NAMES, [])

        brand = sku.get(keys.BRAND)

        # for example,
        # for brand loreal excellence intense
        # possible_subcats will be a union of possible_subcats for all start combinations
        # ["loreal", "loreal excellence", "loreal excellence intense"]
        possible_subcats_for_this_brand = []
        if brand:
            brand_tokens = brand.split()
            for i in range(1, len(brand_tokens) + 1):
                possible_parent_brand = " ".join(brand_tokens[0:i])
                possible_subcats_for_this_brand += brand_subcats_pairs.get(
                    possible_parent_brand, []
                )

        for sub in itertools.chain(
                sku.get(keys.CLEAN_SUBCATS, []), possible_subcats_for_this_brand
        ):
            if any(sub in name for name in clean_names):
                sub_cat_candidates.append(sub)

        # dedup, remove very long sub_cats, they are mostly wrong, remove if it's also a brand
        sub_cat_candidates = list(
            set(s for s in sub_cat_candidates
                if s and len(s) < 30 and "indirim" not in s and s not in brand_subcats_pairs)
        )

        sku[keys.SUBCAT_CANDIDATES] = sub_cat_candidates
        if sub_cat_candidates:
            sku[keys.SUBCAT] = select_subcat(sub_cat_candidates, sub_cat_market_pairs)

    return skus


def create_subcat_index():
    brand_subcats_pairs = services.read_json(brand_subcats_pairs_path)

    subcat_index = defaultdict(dict)
    stopwords = {"ml", "gr", "adet", "ve", "and", "ile"}

    for brand, subcats in brand_subcats_pairs.items():
        subcat_index[brand] = services.create_inverted_index(set(subcats), stopwords)

    services.save_json(output_dir / "subcat_index.json", subcat_index)


def create_indexes():
    (
        brand_subcats_pairs,
        clean_brand_original_brand_pairs,
        sub_cat_market_pairs,
    ) = index_brands_and_subcats()

    sub_cat_market_pairs = services.convert_dict_set_values_to_list(
        sub_cat_market_pairs
    )
    services.save_json(output_dir / "sub_cat_market_pairs.json", sub_cat_market_pairs)

    brand_subcats_pairs = services.convert_dict_set_values_to_list(brand_subcats_pairs)
    services.save_json(brand_subcats_pairs_path, brand_subcats_pairs)
    services.save_json(
        output_dir / "clean_brand_original_brand_pairs.json",
        clean_brand_original_brand_pairs,
    )

    return brand_subcats_pairs, sub_cat_market_pairs


def add_brand_and_subcat(clean_skus: List[dict]):
    """
    brand and subcats are together because a brand restricts the possible subcats

    1. clean and index brands + cats
        brand_subcats_pairs,
        clean_brand_original_brand_pairs,
        sub_cat_market_pairs,
    2. select a brand
        skus_with_brands
    3. select a category by restricting possible cats for this brand and prioritizing markets
        skus_with_brand_and_sub_cat
    """
    brand_subcats_pairs, sub_cat_market_pairs = create_indexes()

    # add brand
    skus_with_brands = add_brand_to_skus(clean_skus, brand_subcats_pairs)

    # add subcat
    skus_with_brand_and_sub_cat = add_sub_cat_to_skus(
        skus_with_brands, brand_subcats_pairs, sub_cat_market_pairs
    )

    return skus_with_brand_and_sub_cat


def count_fields(docs, target_key):
    return sum(1 if target_key in doc else 0 for doc in docs)


def inspect_results():
    docs = services.read_json(output_dir / "name_brand_subcat.json")

    with_brand_only = [
        doc for doc in docs if keys.BRAND in doc and keys.SUBCAT not in doc
    ]
    services.save_json(output_dir / "with_brand_only.json", with_brand_only)

    with_subcat_only = [
        doc for doc in docs if keys.BRAND not in doc and keys.SUBCAT in doc
    ]
    services.save_json(output_dir / "with_subcat_only.json", with_subcat_only)

    with_brand_and_sub = [
        doc for doc in docs if keys.BRAND in doc and keys.SUBCAT in doc
    ]
    services.save_json(output_dir / "with_brand_and_sub.json", with_brand_and_sub)

    brands_in_results = [doc.get(keys.BRAND) for doc in docs]
    subcats_in_results = [doc.get(keys.SUBCAT) for doc in docs]

    services.save_json(
        output_dir / "brands_in_results.json",
        sorted(services.dedup_denull(brands_in_results)),
    )
    services.save_json(
        output_dir / "subcats_in_results.json",
        sorted(services.dedup_denull(subcats_in_results)),
    )

    with_brand = count_fields(docs, keys.BRAND)
    with_sub = count_fields(docs, keys.SUBCAT)

    print(
        "total",
        len(docs),
        "\n",
        "with_brand",
        with_brand,
        "\n",
        "with_sub",
        with_sub,
        "\n",
        "with_subcat_only",
        len(with_subcat_only),
        "\n",
        "with_brand_only",
        len(with_brand_only),
        "\n",
        "with_both_brand_and_subcat",
        len(with_brand_and_sub),
        "\n",
    )


def add_gender(sku):
    men = {"erkek", "men", "bay", "man"}
    woman = {"kadin", "women", "bayan", "woman"}
    child = {"cocuk", "child", "children"}
    unisex = {"unisex"}


def add_color(sku):
    ...


def add_sub_brand(sku):
    ...


def refresh():
    """
    run the data enrichment from scratch
    """
    skus = services.read_json(input_dir / "full_skus.json").values()
    clean_skus = get_clean_skus(skus)
    skus_with_brand_and_sub_cat = add_brand_and_subcat(clean_skus)
    services.save_json(
        output_dir / "skus_with_brand_and_sub_cat.json", skus_with_brand_and_sub_cat
    )

    name_brand_subcat = get_sku_summary(skus_with_brand_and_sub_cat)
    services.save_json(output_dir / "name_brand_subcat.json", name_brand_subcat)

    inspect_results()
    print("done!")


def test_brands():
    # brand_pool = services.read_json(output_dir / "brand_pool.json")

    skus = services.read_json(input_dir / "full_skus.json").values()
    names = [sku.get(keys.CLEAN_NAMES, []) for sku in skus]
    token_lists = get_token_lists(names)
    first_n_tokens = [" ".join(tokens[0:5]) for tokens in token_lists]
    filtered_tokens = [token for token in first_n_tokens if len(token) > 2]
    freq = OrderedDict(Counter(filtered_tokens).most_common())
    services.save_json(output_dir / "name_freq_first_5.json", freq)


def test_sub_brand():
    """ test to find sub brands """

    brand_pool = services.read_json(output_dir / "brand_pool.json")
    name_brand_subcat = services.read_json(output_dir / "name_brand_subcat.json")

    path = output_dir / "most_frequent_start_strings.json"
    freq = services.read_json(path)

    for doc in name_brand_subcat:
        brand = doc.get(keys.BRAND, "")
        if not brand:
            continue

        brand_tokens = brand.split()
        if len(brand_tokens) == 1:
            continue
        brand_freq = {}
        for i in range(1, len(brand_tokens)):
            root = " ".join(brand_tokens[:i])
            if root in brand_pool:
                count = freq.get(root, 0)
                brand_freq[root] = count

        root_brand = services.get_most_frequent_key(brand_freq)
        if root_brand:
            print((brand, root_brand))
            doc[keys.BRAND] = root_brand
            doc[keys.SUB_BRAND] = brand

    print("with_subbrand", count_fields(name_brand_subcat, keys.SUB_BRAND))
    services.save_json(output_dir / "with_subbrand.json", name_brand_subcat)


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)
    brand_subcats_pairs_path = output_dir / "brand_subcats_pairs.json"
    refresh()
    # inspect_brands()
    # test_brands()
    # test_sub_brand()
    """ 
    TODO next 
    
    get freq straight 
    
    if a root brand exists, it is the brand, and later one is subbrand
    
    remove size, brand, cat, color, gender
    

    """
