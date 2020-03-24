import constants as keys
import data_services
from data_models import MatchingMechanism
from services import json_util
from supermatch import create_matching
from test.test_logs.paths import get_paths
from test.excel.excel import create_excel
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


def save_case_results(name, docs, matching_collection):
    paths = get_paths(name)

    create_excel(cursor=docs, excel_path=paths.excel_path)

    json_util.save_json(paths.full_docs_path, docs)
    json_util.save_json(paths.products_path, matching_collection.products)
    json_util.save_json(paths.skus_path, matching_collection.skus)


def get_docs_with_ids(matching_collection):
    docs = list()
    for doc_id, sku_and_product_ids in matching_collection.id_tree.items():
        if "+clone" in doc_id:
            # skip cloned docs
            continue
        doc = matching_collection.id_doc_pairs.get(doc_id)
        doc = {**doc, **sku_and_product_ids}
        docs.append(doc)

    return docs


def run_matcher(name, links, links_of_products=None):
    query = {keys.LINK: {"$in": links}}
    docs_to_match = data_services.get_docs_to_match(query)

    matching_collection = create_matching(
        docs_to_match=docs_to_match, links_of_products=links_of_products
    )
    docs = get_docs_with_ids(matching_collection)
    save_case_results(name, docs, matching_collection)


def palette():
    name = ("palette",)
    links = (json_util.read_json("pal.json"),)
    links_of_products = data_services.get_links_of_products()
    run_matcher(name, links, links_of_products)


def full():
    paths = get_paths("f2")
    id_doc_pairs = json_util.read_json(paths.id_doc_pairs_path)
    docs_to_match = list()
    for id, doc in id_doc_pairs.items():
        doc["_id"] = id
        docs_to_match.append(doc)

    matching_mechanism = MatchingMechanism(barcode=True, promoted=True, exact_name=True)
    links_of_products = data_services.get_links_of_products()
    matching_collection = create_matching(
        docs_to_match, matching_mechanism, links_of_products
    )
    docs = get_docs_with_ids(matching_collection)
    save_case_results("full", docs, matching_collection)


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    name = "migros_seker"
    links = get_links("https://www.migros.com.tr/dogus-toz-seker-5-kg-p-3285bd")
    run_matcher(name=name, links=links)
    # test_palette()
    # test_full()
