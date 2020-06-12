import collections
from dataclasses import asdict
from collections import Counter

import services
import constants as keys
from spec.model.sku import SKU
from spec.exceptions import MatchingException
from supermatch.id_selector import select_unique_id


def get_name_priorities():
    return {
        keys.GRATIS: 8,
        keys.TRENDYOL: 7,
        keys.WATSONS: 7,
        keys.MIGROS: 6,
        keys.A101: 5,
        keys.CEPTESOK: 4,
        keys.EVESHOP: 3,
        keys.ROSSMANN: 2,
        keys.CARREFOUR: 1,
    }


def get_image_priorities():
    return {
        keys.GRATIS: 8,
        keys.MIGROS: 7,
        keys.TRENDYOL: 7,
        keys.CARREFOUR: 6,
        keys.A101: 5,
        keys.CEPTESOK: 4,
        keys.EVESHOP: 3,
        keys.ROSSMANN: 2,
        keys.WATSONS: -1,
    }


def get_name(names):
    name_priorities = get_name_priorities()
    name_priority = -2
    selected_name = ""
    for market, name in names.items():
        if name_priorities.get(market, 0) > name_priority:
            name_priority = name_priorities.get(market, 0)
            selected_name = name

    return selected_name


def get_image(docs):
    image_priorities = get_image_priorities()
    image_priority = -2
    images = {doc.get(keys.MARKET): doc.get(keys.SRC) for doc in docs}
    selected_image = None
    for market, image in images.items():
        if image_priorities.get(market, 0) > image_priority:
            selected_image = image
            image_priority = image_priorities.get(market, 0)
    return selected_image


def get_prices(docs):
    prices = {
        doc.get(keys.MARKET): doc.get(keys.PRICE)
        for doc in docs
        if doc.get(keys.OUT_OF_STOCK) not in [True, "Stokta Yok"]
    }
    prices = {
        market: price
        for market, price in prices.items()
        if market in keys.VISIBLE_MARKETS
    }
    prices = {market: services.convert_price(price) for market, price in prices.items()}
    prices = {market: price for market, price in prices.items() if price}
    if not prices:
        raise MatchingException("no prices")

    min_price = min(prices.values())
    if any((price > 3 * min_price) for price in prices.values()):
        raise MatchingException("absurd price difference")

    return prices


def get_variant_name(docs):
    """
    variants: [{'250 ml': '/shopping/product/17523461779494271950'}, {}...]
    if any google_doc in sku_docs, get VARIANT_NAME from this google_doc
    """

    variant_names = [
        doc.get(keys.VARIANT_NAME) for doc in docs if keys.VARIANT_NAME in doc
    ]

    variants = [doc.get(keys.VARIANTS, {}) for doc in docs]

    doc_links = [doc.get(keys.LINK) for doc in docs]

    for variant in variants:
        for var_link, variant_name in variant.items():
            if any([var_link in doc_link for doc_link in doc_links]):
                variant_names.append(variant_name)

    if variant_names:
        return variant_names[0]


def reduce_docs_to_sku(docs: list, doc_ids: list, used_ids) -> tuple:
    if not docs:
        return ()

    try:
        prices = get_prices(docs)
    except MatchingException:
        return ()

    sku_ids = (doc.get(keys.SKU_ID) for doc in docs)
    sku_ids = (p for p in sku_ids if p)
    sku_ids_count = dict(collections.Counter(sku_ids))
    sku_id = select_unique_id(sku_ids_count, doc_ids, used_ids)

    names = {
        doc.get(keys.MARKET): doc.get(keys.NAME) for doc in docs if doc.get(keys.NAME)
    }
    sku_name = get_name(names)
    doc_names = list(names.values())

    sku_src = get_image(docs)

    barcodes = [doc.get(keys.BARCODES) for doc in docs]
    barcodes = services.flatten(barcodes)
    barcodes = list(set(barcodes))

    clean_names = list(doc.get("clean_name") for doc in docs)

    tokens = services.tokenize_a_nested_list(clean_names)
    most_common_tokens = sorted(services.get_n_most_common_list_elements(tokens, 3))
    tags = " ".join(sorted(list(set(tokens))))

    markets = list(set(prices.keys()))
    best_price = min(list(prices.values()))

    digits = unit = size = unit_price = None
    digit_unit_tuples = [doc.get(keys.DIGIT_UNIT_TUPLES) for doc in docs]
    digit_unit_tuples = services.flatten(digit_unit_tuples)

    if digit_unit_tuples:
        digits, unit = services.get_most_common_item(digit_unit_tuples)
        size = services.join_digits_units(digits, unit)

    if digits:
        unit_price = round(best_price / digits, 2)

    cats = [doc.get(keys.CATEGORIES) for doc in docs]
    brands = [doc.get(keys.BRAND) for doc in docs]

    # TODO add color
    # TODO add reviews

    sku = SKU(
        doc_ids=doc_ids,
        sku_id=sku_id,
        objectID=sku_id,
        name=sku_name,
        src=sku_src,
        prices=prices,
        markets=markets,
        market_count=len(markets),
        best_price=best_price,
        barcodes=barcodes,
        tags=tags,
        links=list(set(doc.get(keys.LINK) for doc in docs)),
        most_common_tokens=most_common_tokens,
        names=doc_names,
        clean_names=clean_names,
        digits=digits,
        unit=unit,
        size=size,
        unit_price=unit_price,
        digits_units=list(set(digit_unit_tuples)),
        categories=cats,
        brands=brands,
        variant_name=get_variant_name(docs)
    )

    sku = asdict(sku)
    sku = services.remove_nulls_from_list_values_of_a_dict(sku)
    sku = services.remove_null_dict_values(sku)

    return sku, sku_id
