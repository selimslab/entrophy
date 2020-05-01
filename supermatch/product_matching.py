import itertools
import operator
import services


def get_gratis_link_id_tuples(skus: dict, gratis_product_links: set) -> list:
    gratis_links_with_sku = (
        (link, sku_id)
        for sku_id, sku in skus.items()
        for link in sku.get("links", [])
        if "?sku" in link
    )
    gratis_link_id_tuples = [
        (link.split("?")[0], sku_id)
        for (link, sku_id) in gratis_links_with_sku
        if link.split("?")[0] in gratis_product_links
    ]

    return gratis_link_id_tuples


def get_google_groups(skus, variants):
    """
    variants: [{'250 ml': '/shopping/product/17523461779494271950'}, {} ... ]
    """
    # variants = data_services.get_google_variants()

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


def group_link_id_tuples(link_id_tuples):
    sorted_link_id_tuples = sorted(link_id_tuples, key=operator.itemgetter(0))
    raw_groups = itertools.groupby(sorted_link_id_tuples, operator.itemgetter(0))
    groups = (list(map(operator.itemgetter(1), group)) for key, group in raw_groups)
    groups = [list(set(group)) for group in groups]
    return groups


def group_skus(skus: dict, variants, links_of_products) -> list:
    google_groups = get_google_groups(skus, variants)

    gratis_link_id_tuples = get_gratis_link_id_tuples(skus, links_of_products)
    gratis_groups = group_link_id_tuples(gratis_link_id_tuples)

    sku_groups = itertools.chain(google_groups, gratis_groups)

    graph_of_skus = services.GenericGraph.create_graph_from_neighbor_pairs(sku_groups)
    groups_of_sku_ids = services.GenericGraph.create_connected_component_groups(
        graph_of_skus
    )

    return groups_of_sku_ids


if __name__ == "__main__":
    pass