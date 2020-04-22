import constants as keys
import data_services.mongo.collections as collections
import logging


def get_gratis_product_names(product_links: set):
    logging.info("reading names of gratis products..")
    cursor = collections.items_collection.find(
        {keys.MARKET: keys.GRATIS, keys.LINK: {"$in": list(product_links)}},
        {keys.LINK: 1, keys.NAME: 1},
    )
    gratis_product_names = dict()
    for doc in cursor:
        gratis_product_names[doc.get(keys.LINK)] = doc.get(keys.NAME)

    return gratis_product_names


def get_links_of_gratis_products(id_doc_pairs) -> set:
    logging.info("finding gratis product links..")
    gratis_links = (doc.get(keys.LINK) for doc in id_doc_pairs.values() if doc.get(keys.MARKET) == keys.GRATIS)
    clean_links = (link[:-1] if link[-1] == "/" else link for link in set(gratis_links))
    product_links = (link.split("?")[0] for link in clean_links if "?sku" in link)
    links_of_products = (
        link for link in product_links if not link.split("/")[-1].isdigit()
    )
    return set(links_of_products)

