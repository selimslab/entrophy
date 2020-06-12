import logging
import operator
import itertools
import collections
from tqdm import tqdm

import services
import constants as keys


# TODO these 2 functions could be refactored to 4-5 functions and simplified
def get_matches(self, name):
    token_set = name.split()
    candidate_groups = [self.inverted_index.get(token, []) for token in token_set]
    candidate_groups = set(itertools.chain(*candidate_groups))
    if not candidate_groups:
        return

    matches = set()

    for id_group in candidate_groups:
        # TODO iff same sizes

        group_common = self.common_tokens.get(id_group, set())
        if not group_common:
            continue

        # single name must cover all common tokens of the group
        if not token_set.issuperset(group_common):
            continue

        group_all = self.group_tokens.get(id_group, set())

        # the group  must cover all tokens of the single name

        if not group_all.issuperset(token_set):
            continue

        common_set_size, diff_size = (
            len(group_common),
            len(group_all.difference(token_set)),
        )
        # first common, if commons same, difference
        matches.add(
            (
                common_set_size,
                diff_size,
                id_group,
                tuple(group_common),
                tuple(group_all.difference(token_set)),
                name,
                tuple(self.group_names.get(id_group)),
            )
        )

    return matches


def select_a_match(matches):
    # which group has the max number of tokens in common with this name
    max_common_size = max(matches, key=operator.itemgetter(0))[0]
    matches_with_max_common_size = [
        match for match in matches if match[0] == max_common_size
    ]
    if len(matches_with_max_common_size) == 1:
        match = matches_with_max_common_size.pop()
    else:
        match = min(matches_with_max_common_size, key=operator.itemgetter(1))
    return match


def match_singles(self, doc_id, name):
    """ connect single name to a group """

    # a single name could be matched to multiple groups
    matches = get_matches(self, name)

    if not matches:
        return

    match = select_a_match(matches)
    (
        common_set_size,
        diff_size,
        id_group,
        common_set,
        diff_set,
        name,
        group_names,
    ) = match

    self.sku_graph.add_edges_from([(doc_id, id_group[0])])
    self.connected_ids.add(doc_id)
    self.stages[doc_id] = "set_match"

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

    note: passing self to a function is normal and practical here,
    as many examples in python standard libraries
    """

    id_groups = self.create_connected_component_groups(self.sku_graph)

    # filter without barcode
    id_groups = [
        id_group
        for id_group in id_groups
        if all(id in self.connected_ids for id in id_group)
    ]

    self.group_info = collections.defaultdict(dict)
    self.inverted_index = collections.defaultdict(set)

    logging.info("creating inverted index..")

    for id_group in tqdm(id_groups):
        group = dict()
        docs = [self.id_doc_pairs.get(doc_id, {}) for doc_id in id_group if "clone" not in doc_id]

        names = [
            doc.get(keys.CLEAN_NAME)
            for doc in docs
        ]
        names = [n for n in names if n]

        group["names"] = names

        token_sets = [set(name.split()) for name in names]

        # update common_tokens
        commons = set.intersection(*token_sets)
        if commons:
            group["common_tokens"] = commons

        # update group_tokens
        all_tokens = set.union(*token_sets)
        if all_tokens:
            group["tokens"] = all_tokens

        # update inverted_index
        for token in all_tokens:
            self.inverted_index[token].add(tuple(id_group))

        size_tuples = [doc.get(keys.DIGIT_UNIT_TUPLES)
                       for doc in docs]
        group[keys.DIGIT_UNIT_TUPLES] = list(set(services.flatten(size_tuples)))

        self.group_info[tuple(id_group)] = group

    unmatched_ids = set(self.id_doc_pairs.keys()).difference(self.connected_ids)
    single_names = [
        (doc_id, self.id_doc_pairs.get(doc_id, {}).get(keys.CLEAN_NAME))
        for doc_id in unmatched_ids
        if "clone" not in doc_id
    ]
    logging.info("matching singles..")
    # this could be parallel but there are problems with multiprocessing code with class instances
    matched_names = [
        match_singles(self, doc_id, clean_name) for doc_id, clean_name in tqdm(single_names) if clean_name
    ]
    matched_names = [m for m in matched_names if m]

    logging.info("saving matched_names..")
    services.save_json("matched_names.json", matched_names)
