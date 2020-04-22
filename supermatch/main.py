import logging
from typing import Iterator
import constants as keys
from supermatch import id_doc_pairer, sku_grouper
from supermatch.sku_graph import sku_graph_creator
from supermatch.doc_reducer import reduce_docs_to_sku
import uuid
from tqdm import tqdm


def get_sku_groups(id_doc_pairs):
    graph_of_raw_docs = sku_graph_creator.create_graph(id_doc_pairs)

    groups_of_doc_ids = sku_graph_creator.create_connected_component_groups(
        graph_of_raw_docs
    )

    return groups_of_doc_ids


def reduce_docs(groups_of_doc_ids: list, id_doc_pairs: dict) -> dict:
    skus = dict()

    logging.debug("reducing docs to skus..")

    used_ids = set()
    for doc_ids in tqdm(groups_of_doc_ids):
        if len(doc_ids) == 1 and "clone" in doc_ids[0]:
            continue

        docs = [id_doc_pairs.get(doc_id, {}) for doc_id in doc_ids]
        sku = reduce_docs_to_sku(docs, doc_ids, used_ids)
        if sku:
            sku_id = sku.get("sku_id")
            used_ids.add(sku_id)
            skus[sku_id] = sku

            for doc in docs:
                doc[keys.SKU_ID] = sku_id
                doc[keys.PRODUCT_ID] = sku_id

            sku["docs"] = docs
            sku["doc_ids"] = doc_ids

    return skus


def add_product_info(groups_of_sku_ids, skus):
    for sku_ids in groups_of_sku_ids:
        product_id = str(uuid.uuid4())
        for sku_id in sku_ids:
            sku = skus[sku_id]

            sku[keys.VARIANTS] = sku_ids
            sku[keys.PRODUCT_ID] = product_id
            sku[keys.SKU_ID] = sku_id

            docs = sku["docs"]
            for doc in docs:
                doc[keys.PRODUCT_ID] = product_id
            sku["docs"] = docs

            skus[sku_id] = sku

    return skus


def create_matching(
        docs_to_match: Iterator,
        links_of_products: set = None,
        id_doc_pairs=None,
        debug=True,
) -> dict:
    if links_of_products is None:
        links_of_products = set()

    if id_doc_pairs is None:
        id_doc_pairs = id_doc_pairer.create_id_doc_pairs(docs_to_match)

    # don't use gratis products for matching
    id_doc_pairs = {
        doc_id: doc
        for doc_id, doc in id_doc_pairs.items()
        if doc.get(keys.LINK) not in links_of_products
    }

    groups_of_doc_ids = get_sku_groups(id_doc_pairs)
    skus = reduce_docs(groups_of_doc_ids, id_doc_pairs)

    del id_doc_pairs

    if not debug:
        groups_of_sku_ids = sku_grouper.group_skus(skus)
        skus = add_product_info(groups_of_sku_ids, skus)

    skus = {
        sku_id: {k: v for k, v in sku.items() if isinstance(k, str) and v is not None}
        for sku_id, sku in skus.items()
    }

    logging.info(f"skus # {len(skus)}")
    return skus
