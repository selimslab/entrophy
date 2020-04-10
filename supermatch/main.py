import logging
from typing import Iterator
import collections
import constants as keys
from supermatch import id_doc_pairer, sku_grouper
from supermatch.id_selector import select_unique_id
from supermatch.sku_graph import sku_graph_creator
from supermatch.doc_reducer import reduce_docs_to_sku


def create_matching(
        docs_to_match: Iterator,
        links_of_products: set = None
):
    if links_of_products is None:
        links_of_products = set()

    id_doc_pairs = id_doc_pairer.create_id_doc_pairs(docs_to_match)

    # don't use gratis products for matching
    id_doc_pairs = {
        doc_id: doc
        for doc_id, doc in id_doc_pairs.items()
        if doc.get(keys.LINK) not in links_of_products
    }

    graph_of_raw_docs = sku_graph_creator.create_graph(
        id_doc_pairs
    )

    groups_of_doc_ids: Iterator = sku_graph_creator.create_connected_component_groups(
        graph_of_raw_docs
    )

    skus = dict()
    used_sku_ids = set()
    for doc_ids in groups_of_doc_ids:
        docs = [id_doc_pairs.get(doc_id) for doc_id in doc_ids]
        sku = reduce_docs_to_sku(docs, used_sku_ids)
        if sku:
            sku["doc_ids"] = doc_ids
            sku["docs"] = docs
            sku_id = sku.get("sku_id")
            skus[sku_id] = sku
            used_sku_ids.add(sku_id)

    groups_of_sku_ids = sku_grouper.group_skus(skus)

    used_product_ids = set()
    for sku_ids in groups_of_sku_ids:
        product_id_counts = collections.Counter()

        for sku_id in sku_ids:
            sku = skus.get(sku_id)
            sku["options"] = [id for id in sku_ids if id != sku_id]
            product_id_counts.update(sku.get("product_id_counts", {}))
            skus[sku_id] = sku

        product_id = select_unique_id(product_id_counts, used_product_ids, sku_ids)
        for sku_id in sku_ids:
            skus[sku_id]["product_id"] = product_id

        used_product_ids.add(product_id)

    skus = [
        {k: v for k, v in sku.items() if isinstance(k, str) and v is not None}
        for sku in skus.values()
    ]
    skus = [s for s in skus if s]
    logging.info(f"skus # {len(skus)}")

    return skus
