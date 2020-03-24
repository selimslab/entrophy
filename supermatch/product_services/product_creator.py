import itertools
import operator

import constants as keys
import data_services
import services
from .sku_reducer import reduce_skus_to_products


def get_gratis_link_id_tuples(id_sku_pairs: dict, gratis_product_links: set) -> list:
    gratis_links_with_sku = [
        (link, sku_id)
        for sku_id, sku in id_sku_pairs.items()
        for link in sku.get("links", [])
        if "?sku" in link
    ]
    gratis_link_id_tuples = [
        (link.split("?")[0], sku_id)
        for (link, sku_id) in gratis_links_with_sku
        if link.split("?")[0] in gratis_product_links
    ]

    return gratis_link_id_tuples


def get_google_groups(id_sku_pairs):
    """
    variants: [{'250 ml': '/shopping/product/17523461779494271950'}, {} ... ]
    """
    variants = data_services.get_google_variants()

    variant_id_pairs = dict()

    for i, var in enumerate(variants):
        links = sorted(list(var.values()))
        links = [link[:-1] if link[-1] == "/" else link for link in links]
        links = ["https://www.google.com" + link for link in links]
        for link in links:
            variant_id_pairs[link] = i

    google_link_id_tuples = [
        (link, variant_id_pairs.get(link), sku_id)
        for sku_id, sku in id_sku_pairs.items()
        for link in sku.get("links", [])
        if link in variant_id_pairs
    ]

    # sort by variant index
    sorted_link_id_tuples = sorted(google_link_id_tuples, key=operator.itemgetter(1))

    # group by variant index
    raw_groups = itertools.groupby(sorted_link_id_tuples, operator.itemgetter(1))

    # operator.itemgetter(2) gets sku_id
    groups = [list(map(operator.itemgetter(2), group)) for key, group in raw_groups]
    google_groups = [list(set(group)) for group in groups]

    return google_groups


def group_link_id_tuples(link_id_tuples):
    sorted_link_id_tuples = sorted(link_id_tuples, key=operator.itemgetter(0))
    raw_groups = itertools.groupby(sorted_link_id_tuples, operator.itemgetter(0))
    groups = [list(map(operator.itemgetter(1), group)) for key, group in raw_groups]
    groups = [list(set(group)) for group in groups]
    return groups


def create_products(id_sku_pairs: dict) -> list:
    google_groups = get_google_groups(id_sku_pairs)

    gratis_product_links: set = data_services.get_links_of_products()
    gratis_link_id_tuples = get_gratis_link_id_tuples(
        id_sku_pairs, gratis_product_links
    )
    gratis_groups = group_link_id_tuples(gratis_link_id_tuples)

    gratis_product_names = data_services.get_gratis_product_names(gratis_product_links)
    # this sku_id has a product name now
    sku_id_gratis_name_pairs = {
        sku_id: gratis_product_names.get(link)
        for (link, sku_id) in gratis_link_id_tuples
    }

    sku_groups = itertools.chain(google_groups, gratis_groups)

    graph_of_skus = services.GenericGraph.create_graph_from_neighbor_pairs(sku_groups)
    groups_of_sku_ids = services.GenericGraph.create_connected_component_groups(
        graph_of_skus
    )
    products = reduce_skus_to_products(
        id_sku_pairs, groups_of_sku_ids, sku_id_gratis_name_pairs
    )

    return products


if __name__ == "__main__":
    pass
