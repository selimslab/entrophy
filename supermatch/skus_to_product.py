import itertools
import operator
import logging
from typing import List

from tqdm import tqdm

import services
import constants as keys
from .docs_to_sku.indexer import Indexer


def get_gratis_link_id_tuples(skus: dict, gratis_product_links: set) -> List[tuple]:
    """Create tuples to be grouped later
    Returns:
        gratis_link_id_tuples: [(link,id), (link,id) .. ]
    """
    # relevant ones include ?sku
    filtered_gratis_product_links = (
        (link, sku_id)
        for sku_id, sku in skus.items()
        for link in sku.get("links", [])
        if "?sku" in link
    )
    gratis_link_id_tuples = [
        (link.split("?")[0], sku_id)
        for (link, sku_id) in filtered_gratis_product_links
        if link.split("?")[0] in gratis_product_links
    ]

    return gratis_link_id_tuples


def get_google_groups(skus: dict, variants: List[dict]) -> List[list]:
    """Products groups from google shopping

    Args:
        variants: [{'250 ml': '/shopping/product/17523461779494271950'}, {} ... ]

    Returns:
        google_groups: [[ids..], [ids..]]
    """
    variant_id_pairs = dict()

    for i, var in enumerate(variants):
        links = sorted(list(var.keys()))
        links = [link[:-1] if link[-1] == "/" else link for link in links if link]
        links = ["https://www.google.com" + link for link in links]
        for link in links:
            variant_id_pairs[link] = i

    google_link_id_tuples = [
        (link, variant_id_pairs.get(link), sku_id)
        for sku_id, sku in skus.items()
        for link in sku.get("links", [])
        if link in variant_id_pairs
    ]

    # sort by variant index
    sorted_link_id_tuples = sorted(google_link_id_tuples, key=operator.itemgetter(1))

    # group by variant index
    raw_groups = itertools.groupby(sorted_link_id_tuples, operator.itemgetter(1))

    groups = (list(map(operator.itemgetter(2), group)) for key, group in raw_groups)
    google_groups = [list(set(group)) for group in groups]

    return google_groups


def group_link_id_tuples(link_id_tuples: List[tuple]) -> List[list]:
    """ group tuples by index 1
    Example:
    in: [(link1,id3), (link1,id4) .. ]
    out: [ [id3, id4] , .. ]
    """
    sorted_link_id_tuples = sorted(link_id_tuples, key=operator.itemgetter(0))
    raw_groups = itertools.groupby(sorted_link_id_tuples, operator.itemgetter(0))
    # let only ids remain, itemgetter(1) gets the id from (link, id) tuple
    groups = (list(map(operator.itemgetter(1), group)) for key, group in raw_groups)
    groups = [list(set(group)) for group in groups]
    return groups


def set_match_generator_for_skus(skus: dict) -> tuple:
    eligible = {
        sku_id: sku
        for sku_id, sku in skus.items()
        if keys.VARIANT_NAME not in sku and keys.COLOR not in sku
    }
    indexer = Indexer()
    logging.info("creating group_info and inverted index..")
    for sku_id, sku in tqdm(eligible.items()):
        indexer.index_skus(sku, sku_id)

    for sku_id, sku in tqdm(eligible.items()):
        matches = indexer.search_skus_to_connect(sku, sku_id)
        if matches:
            other_sku_id_to_connect = services.get_most_frequent_key(matches)
            # connect to single doc to the first element of id group,
            # since the group is all connected, any member will do
            yield sku_id, other_sku_id_to_connect


def group_skus(skus: dict, variants, links_of_products) -> list:
    google_groups = get_google_groups(skus, variants)

    gratis_link_id_tuples = get_gratis_link_id_tuples(skus, links_of_products)
    gratis_groups = group_link_id_tuples(gratis_link_id_tuples)

    logging.info("creating edges_from_sku_names")
    edges_from_sku_names = set_match_generator_for_skus(skus)
    edges_from_sku_names = list(edges_from_sku_names)
    print(len(edges_from_sku_names), "connections from product set match")

    sku_groups = itertools.chain(google_groups, gratis_groups, edges_from_sku_names)

    graph_of_skus = services.GenericGraph.create_graph_from_neighbor_pairs(sku_groups)
    groups_of_sku_ids = services.GenericGraph.create_connected_component_groups(
        graph_of_skus
    )

    return groups_of_sku_ids


if __name__ == "__main__":
    ...
