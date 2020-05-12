import logging
from typing import Iterator
import constants as keys
from supermatch import id_doc_pairer, product_matching
from supermatch.sku_matching import SKUGraphCreator
from supermatch.doc_reducer import reduce_docs_to_sku
import uuid
from tqdm import tqdm
import data_services


def get_sku_groups(id_doc_pairs, debug):
    sku_graph_creator = SKUGraphCreator(id_doc_pairs)
    graph_of_raw_docs, stages = sku_graph_creator.create_graph(debug)
    groups_of_doc_ids = sku_graph_creator.create_connected_component_groups(
        graph_of_raw_docs
    )

    # add matching stage info to docs
    for doc_id, stage in stages.items():
        id_doc_pairs[doc_id]["stage"] = stage

    for stage in set(stages.values()):
        res = sum(v == stage for v in stages.values())
        print(res, stage)

    return groups_of_doc_ids


def reduce_docs(groups_of_doc_ids: list, id_doc_pairs: dict) -> dict:
    skus = dict()

    logging.debug("reducing docs to skus..")

    used_ids = set()

    # this could be parallel
    for doc_ids in tqdm(groups_of_doc_ids):
        if len(doc_ids) == 1 and "clone" in doc_ids[0]:
            continue

        docs = [id_doc_pairs.pop(doc_id, {}) for doc_id in doc_ids]
        sku, sku_id = reduce_docs_to_sku(docs, doc_ids, used_ids)
        if sku:
            used_ids.add(sku_id)
            skus[sku_id] = sku
    return skus


def add_product_info(groups_of_sku_ids, skus):
    for sku_ids in groups_of_sku_ids:
        product_id = str(uuid.uuid4())
        for sku_id in sku_ids:
            skus[sku_id][keys.PRODUCT_ID] = product_id
    return skus


def create_matching(docs_to_match: Iterator, id_doc_pairs=None, debug=False) -> dict:
    if id_doc_pairs is None:
        id_doc_pairs = id_doc_pairer.create_id_doc_pairs(docs_to_match)

    links_of_products = data_services.get_links_of_gratis_products(id_doc_pairs)
    # don't use gratis products for doc grouping
    id_doc_pairs = {
        doc_id: doc
        for doc_id, doc in id_doc_pairs.items()
        if doc.get(keys.LINK) not in links_of_products
    }
    logging.info("finding variants..")
    variants = (doc.get(keys.VARIANTS) for doc in id_doc_pairs.values())
    variants = [v for v in variants if v]

    groups_of_doc_ids = get_sku_groups(id_doc_pairs, debug)
    skus = reduce_docs(groups_of_doc_ids, id_doc_pairs)

    logging.info(f"skus # {len(skus)}")

    logging.info("grouping skus into products..")
    groups_of_sku_ids = product_matching.group_skus(skus, variants, links_of_products)
    skus = add_product_info(groups_of_sku_ids, skus)

    skus = {
        sku_id: {k: v for k, v in sku.items() if isinstance(k, str) and v is not None}
        for sku_id, sku in skus.items()
    }

    logging.info(f"skus # {len(skus)}")
    return skus
