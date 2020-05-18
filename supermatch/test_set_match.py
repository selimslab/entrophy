import random
import logging
import services

from .set_match import set_match


def get_expected_neighbours(self, id_groups):
    # select 1 from a group, remove the edge, remove from connected, and later check if its matched
    expected_neighbors = {}
    for g in id_groups:
        sample_size = 1 if len(g) < 5 else 2
        test_nodes = random.sample(g, sample_size)
        for test_node in test_nodes:
            g.remove(test_node)
            self.connected_ids.remove(test_node)
            edges_of_test_node = self.sku_graph.edges(test_node)
            self.sku_graph.remove_edges_from(list(edges_of_test_node))

        for test_node in test_nodes:
            expected_neighbors[test_node] = g

    return expected_neighbors


def test_set_match(self):
    id_groups = self.create_connected_component_groups(self.sku_graph)
    id_groups = [[id for id in id_group if "clone" not in id] for id_group in id_groups]
    id_groups = [g for g in id_groups if len(g) >= 3]

    expected_neighbors = get_expected_neighbours(self, id_groups)

    self.exact_name_match()
    set_match(self)

    ok = set()
    matched_to_another_group = set()
    id_groups = self.create_connected_component_groups(self.sku_graph)
    for g in id_groups:
        for node in g:
            if node in expected_neighbors:
                expected = expected_neighbors.get(node)
                if set(g).issuperset(set(expected)):
                    expected_neighbors.pop(node)
                    ok.add(node)
                else:
                    matched_to_another_group.add(node)

    # the remaining in check_table failed
    logging.info(f"{len(ok)} is ok, {len(expected_neighbors)} is failed")

    def get_name_and_cleaned_name(id):
        doc = self.id_doc_pairs.get(id)
        name = doc.get("name")
        clean_name = doc.get("clean_name")
        return name, clean_name

    failed_names = {}
    for test_node_id, group in expected_neighbors.items():
        group_names = tuple(get_name_and_cleaned_name(id) for id in group)
        failed_names[str(get_name_and_cleaned_name(test_node_id))] = group_names

    services.save_json("failed_names.json", failed_names)
