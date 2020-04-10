import constants as keys
import data_services
from services import json_util
from supermatch.main import create_matching
from test.test_logs.paths import get_paths
# from test.excel.excel import create_excel
import data_services.mongo.collections as collections

import logging
import sys


def get_links(link):
    doc = collections.items_collection.find_one({keys.LINK: link})
    links = []

    sku_id = doc.get(keys.SKU_ID)
    if sku_id:
        sku_group = collections.items_collection.find({keys.SKU_ID: sku_id})
        links += [doc.get(keys.LINK) for doc in sku_group]

    product_id = doc.get(keys.PRODUCT_ID)
    if product_id:
        product_group = collections.items_collection.find({keys.PRODUCT_ID: product_id})
        links += [doc.get(keys.LINK) for doc in product_group]

    print("SKU_ID and PRODUCT_ID", sku_id, product_id)
    links = list(set(links))
    return links


def get_docs_with_ids(skus):
    alldocs = list()
    for sku_id, sku in skus.items():
        docs = sku.get("docs")
        ids = {keys.SKU_ID: sku_id, keys.PRODUCT_ID: sku.get(keys.PRODUCT_ID)}
        for doc in docs:
            if "clone" in doc.get("_id"):
                continue
            doc = {**doc, **ids}
            alldocs.append(doc)

    return alldocs


def palette():
    name = ("palette",)
    links = (json_util.read_json("pal.json"),)
    links_of_products = data_services.get_links_of_products()
    # run_matcher(name, links, links_of_products)


def full():
    paths = get_paths("f2")
    id_doc_pairs = json_util.read_json(paths.id_doc_pairs_path)
    docs_to_match = list()
    for id, doc in id_doc_pairs.items():
        doc["_id"] = id
        docs_to_match.append(doc)

    links_of_products = data_services.get_links_of_products()
    matching_collection = create_matching(
        docs_to_match, links_of_products
    )
    docs = get_docs_with_ids(matching_collection)


if __name__ == "__main__":

# test_palette()
# test_full()
