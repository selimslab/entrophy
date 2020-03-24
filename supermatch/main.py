import logging
from typing import Iterator

import constants as keys
import services
import supermatch.sku_services as sku_services
from data_models import MatchingMechanism, MatchingCollection
from supermatch.id_tree_creator import create_id_tree
from supermatch.product_services import product_creator
from supermatch import id_doc_pairer


def get_groups_of_doc_ids(id_doc_pairs, matching_mechanism):
    graph_of_raw_docs = sku_services.sku_graph_creator.create_graph(
        id_doc_pairs, matching_mechanism
    )

    groups_of_doc_ids: Iterator = sku_services.sku_graph_creator.create_connected_component_groups(
        graph_of_raw_docs
    )
    return groups_of_doc_ids


def create_matching(
    docs_to_match: Iterator,
    matching_mechanism: MatchingMechanism = None,
    links_of_products: set = None,
):
    if matching_mechanism is None:
        matching_mechanism = MatchingMechanism(
            barcode=True, promoted=True, exact_name=True
        )
    if links_of_products is None:
        links_of_products = set()

    id_doc_pairs = id_doc_pairer.create_id_doc_pairs(docs_to_match)

    # don't use gratis products for matching
    id_doc_pairs = {
        doc_id: doc
        for doc_id, doc in id_doc_pairs.items()
        if doc.get(keys.LINK) not in links_of_products
    }
    groups_of_doc_ids = get_groups_of_doc_ids(id_doc_pairs, matching_mechanism)

    sku_id_doc_ids_pairs: dict = sku_services.get_sku_id_doc_ids_pairs(
        groups_of_doc_ids, id_doc_pairs
    )

    id_sku_pairs = dict()
    for sku_id, doc_ids in sku_id_doc_ids_pairs.items():
        docs = [id_doc_pairs.get(doc_id) for doc_id in doc_ids]
        sku = sku_services.create_a_single_sku_doc_from_item_docs(docs, sku_id)
        if sku:
            id_sku_pairs[sku_id] = sku

    # id_sku_pairs = NodeSimilarity.add_similarity(id_sku_pairs)

    skus = list(id_sku_pairs.values())
    skus = [services.sanitize_dict(sku) for sku in skus]
    skus = [sku for sku in skus if sku]
    logging.info(f"skus # {len(skus)}")

    products: list = product_creator.create_products(id_sku_pairs)
    products = [services.sanitize_dict(dict(product)) for product in products]
    products = [p for p in products if p]

    logging.info(f"products # {len(products)}")

    id_tree = create_id_tree(sku_id_doc_ids_pairs, products)

    matching_collection = MatchingCollection(
        skus=skus, products=products, id_tree=id_tree
    )

    return matching_collection
