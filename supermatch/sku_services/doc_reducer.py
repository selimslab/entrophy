import collections
from dataclasses import asdict
import services
import constants as keys
from data_models import SKU
from services import convert_price
from services import token_util
from supermatch.exceptions import MatchingException


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
        if market not in keys.HELPER_MARKETS
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


def create_a_single_sku_doc_from_item_docs(docs: list, sku_id: str) -> dict:
    if not docs:
        return {}

    try:
        prices = get_prices(docs)
    except MatchingException:
        return {}

    markets = list(set(prices.keys()))
    market_count = len(markets)
    best_price = min(list(prices.values()))

    barcodes = [doc.get(keys.BARCODES) for doc in docs]
    barcodes = services.flatten(barcodes)
    barcodes = [b for b in barcodes if b]
    sku_barcode = list(set(barcodes))

    sku_ids = [doc.get(keys.SKU_ID) for doc in docs]
    product_ids = [doc.get(keys.PRODUCT_ID) for doc in docs]

    sku_ids = [s for s in sku_ids if s]
    product_ids = [p for p in product_ids if p]

    sku_ids = dict(collections.Counter(sku_ids))
    product_ids = dict(collections.Counter(product_ids))

    links = [doc.get(keys.LINK) for doc in docs]
    links = list(set(links))

    names = {
        doc.get(keys.MARKET): doc.get(keys.NAME) for doc in docs if doc.get(keys.NAME)
    }
    selected_name = get_name(names)

    tags, most_common_tokens = get_tags(names)

    selected_image = get_image(docs)

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
            if str(d) in selected_name:
                digits, unit, size = (d, u, s)
                break
        if size_info and not digits:
            digits, unit, size = size_info[0]

    unit_price = None
    if digits:
        unit_price = round(best_price / digits, 2)

    sku = SKU(
        name=selected_name,
        objectID=sku_id,
        prices=prices,
        markets=markets,
        market_count=market_count,
        best_price=best_price,
        unit_price=unit_price,
        links=links,
        src=selected_image,
        digits=digits,
        unit=unit,
        size=size,
        tags=tags,
        sku_ids_count=sku_ids,
        product_ids_count=product_ids,
        barcodes=sku_barcode,
    )

    return asdict(sku)
