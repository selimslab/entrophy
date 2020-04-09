import collections
from dataclasses import asdict
import services
import constants as keys
from spec.model.sku import SKU
from services import convert_price
from services import token_util
from spec.exceptions import MatchingException
from supermatch.id_selector import select_unique_id


def clean_price(price):
    try:
        if isinstance(price, str):
            price = price.replace("TL", "").replace("₺", "").replace(" ", "").strip()
        return convert_price(price)
    except (TypeError, ValueError) as e:
        print(e)
        return None


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
        if "html" not in name and name_priorities.get(market, 0) > name_priority:
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


def get_tags(names):
    tokens = token_util.get_tokens_of_a_group(list(names.values()))
    most_common_tokens = token_util.get_n_most_common_tokens(tokens, 3).sort()
    unique_tokens = list(set(tokens))
    tags = " ".join(sorted(unique_tokens))
    return tags, most_common_tokens


def get_prices(docs):
    prices = {
        doc.get(keys.MARKET): doc.get(keys.PRICE)
        for doc in docs
        if not doc.get(keys.OUT_OF_STOCK)
    }
    prices = {
        market: price
        for market, price in prices.items()
        if market in keys.VISIBLE_MARKETS
    }

    prices = {market: clean_price(price) for market, price in prices.items()}
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
        doc.get(keys.VARIANT_NAME) for doc in docs if doc.get(keys.VARIANT_NAME)
    ]

    variants = [doc.get(keys.VARIANTS, {}) for doc in docs]

    doc_links = [doc.get(keys.LINK) for doc in docs]

    for variant in variants:
        for variant_name, var_link in variant.items():
            if any([var_link in doc_link for doc_link in doc_links]):
                variant_names.append(variant_name)

    if variant_names:
        return variant_names[0]


def reduce_docs_to_sku(docs: list, used_sku_ids: set) -> dict:
    if not docs:
        return {}

    sku = SKU()

    try:
        sku.prices = get_prices(docs)
    except MatchingException:
        return {}

    sku.markets = list(set(sku.prices.keys()))
    sku.market_count = len(sku.markets)
    sku.best_price = min(list(sku.prices.values()))

    barcodes = [doc.get(keys.BARCODES) for doc in docs]
    barcodes = services.flatten(barcodes)
    barcodes = [b for b in barcodes if b]
    sku.barcodes = list(set(barcodes))

    sku.doc_ids = [doc.get("_id") for doc in docs]

    sku_ids = [doc.get(keys.SKU_ID) for doc in docs]
    sku_ids = [p for p in sku_ids if p]
    sku_ids_count = dict(collections.Counter(sku_ids))
    sku.sku_id = select_unique_id(sku_ids_count, used_sku_ids, sku.doc_ids)

    product_ids = [doc.get(keys.PRODUCT_ID) for doc in docs]
    product_ids = [p for p in product_ids if p]
    sku.product_ids_count = dict(collections.Counter(product_ids))

    links = [doc.get(keys.LINK) for doc in docs]
    sku.links = list(set(links))

    names = {
        doc.get(keys.MARKET): doc.get(keys.NAME) for doc in docs if doc.get(keys.NAME)
    }
    sku.name = get_name(names)

    sku.tags, sku.most_common_tokens = get_tags(names)

    sku.src = get_image(docs)

    size = None
    digits = None
    unit = None
    variant_name = get_variant_name(docs)
    if variant_name:
        size = variant_name
    else:
        size_info = [
            (doc.get(keys.DIGITS), doc.get(keys.UNIT), doc.get(keys.SIZE))
            for doc in docs
        ]
        size_info = [(d, u, s) for (d, u, s) in size_info if d and u and s]
        for (d, u, s) in size_info:
            if str(d) in sku.name:
                digits, unit, size = (d, u, s)
                break
        if size_info and not digits:
            digits, unit, size = size_info[0]

    sku.digits, sku.unit, sku.size = digits, unit, size

    if digits:
        sku.unit_price = round(sku.best_price / digits, 2)

    return asdict(sku)
