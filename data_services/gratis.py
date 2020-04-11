import constants as keys
import data_services.mongo.collections as collections


def get_gratis_product_names(product_links: set):
    cursor = collections.items_collection.find(
        {keys.MARKET: keys.GRATIS, keys.LINK: {"$in": list(product_links)}},
        {keys.LINK: 1, keys.NAME: 1},
    )
    gratis_product_names = dict()
    for doc in cursor:
        gratis_product_names[doc.get(keys.LINK)] = doc.get(keys.NAME)

    return gratis_product_names


def get_links_of_products() -> set:
    links = collections.items_collection.distinct(keys.LINK, {keys.MARKET: keys.GRATIS})
    clean_links = (link[:-1] if link[-1] == "/" else link for link in links)
    product_links = (link.split("?")[0] for link in clean_links if "?sku" in link)
    links_of_products = (
        link for link in product_links if not link.split("/")[-1].isdigit()
    )

    return set(links_of_products)