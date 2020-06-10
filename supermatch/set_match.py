import logging
import operator
import itertools
import collections
from tqdm import tqdm

from .clean_name import tokenize
import services


# TODO these 2 functions could be refactored to 4-5 functions and simplified


def match_singles(self, id, name):
    """ connect single name to a group """

    token_set = tokenize(name)
    candidate_groups = [self.inverted_index.get(token, []) for token in token_set]
    candidate_groups = set(itertools.chain(*candidate_groups))
    if not candidate_groups:
        return

    matches = set()

    for id_group in candidate_groups:
        group_common = self.common_tokens.get(id_group, set())
        if not group_common:
            continue
        if token_set.issuperset(group_common):
            group_all = self.group_tokens.get(id_group, set())

            if group_all.issuperset(token_set):
                common_set_size, diff_size = (
                    len(group_common),
                    len(group_all.difference(token_set)),
                )
                # first common, if commons same, difference
                matches.add(
                    (
                        common_set_size,
                        diff_size,
                        id,
                        id_group,
                        tuple(group_common),
                        tuple(group_all.difference(token_set)),
                        name,
                        tuple(self.group_names.get(id_group)),
                    )
                )
    if matches:
        max_common_size = max(matches, key=operator.itemgetter(0))[0]
        matches_with_max_common_size = [
            match for match in matches if match[0] == max_common_size
        ]
        if len(matches_with_max_common_size) > 1:
            match = min(matches_with_max_common_size, key=operator.itemgetter(1))
        else:
            match = matches_with_max_common_size.pop()

        (
            common_set_size,
            diff_size,
            id,
            id_group,
            common_set,
            diff_set,
            name,
            group_names,
        ) = match

        self.sku_graph.add_edges_from([(id, id_group[0])])
        self.connected_ids.add(id)
        self.stages[id] = "set_match"

        return name, group_names, common_set, diff_set


def set_match(self):
    """
    1. tokenize item names
    2. tokenize already grouped skus
    3. for every group
        create a common set, tokens common to all names in a group
        create a diff set
    4. if a single name covers the common the set of a group
        and the group covers all tokens in this name, it's a match!


    note: don't be surprised,
    passing self to a function is normal and practical here,
    as many examples in python standard libraries
    """

    id_groups = self.create_connected_component_groups(self.sku_graph)

    # filter without barcode
    id_groups = [
        id_group
        for id_group in id_groups
        if all(id in self.connected_ids for id in id_group)  # len(id_group)>1 and
    ]

    common_tokens = dict()
    group_tokens = dict()
    self.inverted_index = collections.defaultdict(set)
    self.group_names = dict()

    logging.info("creating inverted index..")
    for id_group in tqdm(id_groups):
        names = [
            self.id_doc_pairs.get(id).get("clean_name")
            for id in id_group
            if "clone" not in id
        ]
        names = [n for n in names if n]
        self.group_names[tuple(id_group)] = names
        token_sets = [tokenize(name) for name in names]
        if token_sets:
            commons = set.intersection(*token_sets)
            common_tokens[tuple(id_group)] = commons
            all_tokens = set.union(*token_sets)
            group_tokens[tuple(id_group)] = all_tokens
            for token in all_tokens:
                self.inverted_index[token].add(tuple(id_group))

    # filter empty sets
    self.common_tokens = {k: v for k, v in common_tokens.items() if v}
    self.group_tokens = {k: v for k, v in group_tokens.items() if v}

    unmatched_ids = set(self.id_doc_pairs.keys()).difference(self.connected_ids)
    single_names = [
        (id, self.id_doc_pairs.get(id).get("clean_name"))
        for id in unmatched_ids
        if "clone" not in id
    ]
    logging.info("matching singles..")
    # TODO here is a bottleneck
    # this could be parallel but cloud server has problems with multiprocessing code
    matched_names = [
        match_singles(self, id, name) for id, name in tqdm(single_names) if name
    ]
    matched_names = [m for m in matched_names if m]

    logging.info("saving matched_names..")
    services.save_json("matched_names.json", matched_names)
