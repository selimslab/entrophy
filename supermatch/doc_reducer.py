import collections
from dataclasses import asdict
import services
import constants as keys
from spec.model.sku import SKU
from services import convert_price
from services import token_util
from spec.exceptions import MatchingException
from supermatch.id_selector import select_unique_id
from services import name_cleaner
from supermatch.sizing.main import size_finder, SizingException
import logging


def get_size(sku_name, docs):
    digits = unit = size = None

    variant_name = get_variant_name(docs)
    if variant_name:
        return digits, unit, variant_name

    try:
        size_name = name_cleaner.size_cleaner(sku_name)
        result = size_finder.get_digits_and_unit(size_name)
        if result:
            return result
    except SizingException:
        pass

    return digits, unit, size


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


def reduce_docs_to_sku(docs: list, used_sku_ids: set, doc_ids: list) -> dict:
    if not docs:
        return {}

    try:
        prices = get_prices(docs)
    except MatchingException:
        return {}

    markets = list(set(prices.keys()))
    market_count = len(markets)
    best_price = min(list(prices.values()))

    sku_ids = (doc.get(keys.SKU_ID) for doc in docs)
    sku_ids = (p for p in sku_ids if p)
    sku_ids_count = dict(collections.Counter(sku_ids))
    sku_id = select_unique_id(sku_ids_count, used_sku_ids, doc_ids)

    names = {
        doc.get(keys.MARKET): doc.get(keys.NAME) for doc in docs if doc.get(keys.NAME)
    }
    sku_name = get_name(names)

    sku_src = get_image(docs)

    sku = SKU(
        doc_ids=doc_ids,
        sku_id=sku_id,
        product_id=sku_id,
        objectID=sku_id,
        name=sku_name,
        src=sku_src,
        prices=prices,
        markets=markets,
        market_count=market_count,
        best_price=best_price,
    )

    barcodes = [doc.get(keys.BARCODES) for doc in docs]
    barcodes = services.flatten(barcodes)
    barcodes = [b for b in barcodes if b]
    sku.barcodes = list(set(barcodes))

    links = [doc.get(keys.LINK) for doc in docs]
    sku.links = list(set(links))

    tokens = token_util.get_tokens_of_a_group(list(names.values()))
    sku.most_common_tokens = sorted(token_util.get_n_most_common_tokens(tokens, 3))
    sku.tags = " ".join(sorted(list(set(tokens))))

    sku.digits, sku.unit, sku.size = get_size(sku.name, docs)

    if sku.digits:
        sku.unit_price = round(sku.best_price / sku.digits, 2)

    return asdict(sku)
