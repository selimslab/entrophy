import collections
from dataclasses import asdict
import services
import constants as keys
from spec.model.sku import SKU
from services import convert_price
from services import token_util
from spec.exceptions import MatchingException
from supermatch.id_selector import select_unique_id


def get_name_priorities():
    return {
        keys.GRATIS: 8,
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
    prices = {market: convert_price(price) for market, price in prices.items()}
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


def select_size(docs, sku_name):
    digits = unit = size = None
    variant_name = get_variant_name(docs)
    if variant_name:
        size = variant_name

    candidates = [(doc.get(keys.DIGITS), doc.get(keys.UNIT)) for doc in docs]
    for candidate_digits, unit in candidates:
        if str(candidate_digits) in sku_name:
            digits = candidate_digits
            break

    if candidates and not digits:
        digits, unit = collections.Counter(candidates).most_common(1)[0][0]

    if not size and digits and unit:
        size = " ".join([str(digits), unit])

    return digits, unit, size, candidates


def reduce_docs_to_sku(docs: list, doc_ids: list, used_ids) -> tuple:
    if not docs:
        return ()

    try:
        prices = get_prices(docs)
    except MatchingException:
        return ()

    markets = list(set(prices.keys()))
    market_count = len(markets)
    best_price = min(list(prices.values()))

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

    tokens = token_util.get_tokens_of_a_group(clean_names)
    most_common_tokens = sorted(token_util.get_n_most_common_tokens(tokens, 3))
    tags = " ".join(sorted(list(set(tokens))))

    links = [doc.get(keys.LINK) for doc in docs]
    links = list(set(links))

    digits, unit, size, all_digits_units = select_size(docs, sku_name)
    all_digits_units = list(set(tuple(c) for c in all_digits_units))
    unit_price = None
    if digits:
        unit_price = round(best_price / digits, 2)

    cats = [doc.get(keys.CATEGORIES) for doc in docs]
    brands = [doc.get(keys.BRAND) for doc in docs]

    sku = SKU(
        doc_ids=doc_ids,
        sku_id=sku_id,
        objectID=sku_id,
        name=sku_name,
        src=sku_src,
        prices=prices,
        markets=markets,
        market_count=market_count,
        best_price=best_price,
        barcodes=barcodes,
        tags=tags,
        links=links,
        most_common_tokens=most_common_tokens,
        names=doc_names,
        clean_names=clean_names,
        digits=digits,
        unit=unit,
        size=size,
        unit_price=unit_price,
        digits_units=all_digits_units,
        categories=cats,
        brands=brands,
    )

    sku = asdict(sku)
    sku = services.remove_nulls_from_list_values_of_a_dict(sku)
    sku = services.remove_null_dict_values(sku)

    return sku, sku_id
