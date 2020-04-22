import logging
from typing import Iterator
import constants as keys
from supermatch import id_doc_pairer, sku_grouper
from supermatch.sku_graph import sku_graph_creator
from supermatch.doc_reducer import reduce_docs_to_sku
import uuid
from tqdm import tqdm
from memory_profiler import profile
import data_services


def get_sku_groups(id_doc_pairs):
    graph_of_raw_docs = sku_graph_creator.create_graph(id_doc_pairs)

    groups_of_doc_ids = sku_graph_creator.create_connected_component_groups(
        graph_of_raw_docs
    )

    return groups_of_doc_ids


def reduce_docs(groups_of_doc_ids: list, id_doc_pairs: dict, debug=True) -> dict:
    skus = dict()

    logging.debug("reducing docs to skus..")

    used_ids = set()
    for doc_ids in tqdm(groups_of_doc_ids):
        if len(doc_ids) == 1 and "clone" in doc_ids[0]:
            continue

        docs = [id_doc_pairs.pop(doc_id, {}) for doc_id in doc_ids]
        sku, sku_id = reduce_docs_to_sku(docs, doc_ids, used_ids)
        if sku:
            used_ids.add(sku_id)
            skus[sku_id] = sku

            if debug:
                for doc in docs:
                    doc[keys.SKU_ID] = sku_id
                    doc[keys.PRODUCT_ID] = sku_id
                sku["docs"] = docs

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


@profile
def create_matching(
        docs_to_match: Iterator,
        id_doc_pairs=None,
        debug=True,
) -> dict:
    if id_doc_pairs is None:
        id_doc_pairs = id_doc_pairer.create_id_doc_pairs(docs_to_match)

    links_of_products = data_services.get_links_of_gratis_products(id_doc_pairs)
    # don't use gratis products for matching
    id_doc_pairs = {
        doc_id: doc
        for doc_id, doc in id_doc_pairs.items()
        if doc.get(keys.LINK) not in links_of_products
    }
    logging.info("finding variants..")
    variants = (doc.get(keys.VARIANTS) for doc in id_doc_pairs.values())
    variants = (v for v in variants if v)

    groups_of_doc_ids = get_sku_groups(id_doc_pairs)
    skus = reduce_docs(groups_of_doc_ids, id_doc_pairs, debug)

    if not debug:
        groups_of_sku_ids = sku_grouper.group_skus(skus, variants, links_of_products)
        skus = add_product_info(groups_of_sku_ids, skus)

    skus = {
        sku_id: {k: v for k, v in sku.items() if isinstance(k, str) and v is not None}
        for sku_id, sku in skus.items()
    }

    logging.info(f"skus # {len(skus)}")
    return skus
