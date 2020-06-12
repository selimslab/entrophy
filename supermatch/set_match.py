import logging
import operator
import itertools
import collections
from tqdm import tqdm

import services
import constants as keys

from .clean_name import remove_stopwords


# TODO these 2 functions could be refactored to 4-5 functions and simplified


def filter_tokens(s):
    try:
        tokens = s.split()
        tokens = remove_stopwords(tokens)
        tokens = set(t for t in set(tokens) if len(t) > 1 or t.isdigit())
        return tokens
    except AttributeError as e:
        logging.error(e)
        return set()


def get_matches(self, name):
    token_set = filter_tokens(name)
    candidate_groups = [self.inverted_index.get(token, []) for token in token_set]
    candidate_groups = set(itertools.chain(*candidate_groups))
    if not candidate_groups:
        return

    matches = set()

    for id_group in candidate_groups:
        group_common = self.common_tokens.get(id_group, set())
        if not group_common:
            continue
        if not token_set.issuperset(group_common):
            continue

        group_all = self.group_tokens.get(id_group, set())

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


def match_singles(self, doc_id, name):
    """ connect single name to a group """

    matches = get_matches(self, name)

    if not matches:
        return

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


def get_names(id_group, id_doc_pairs):
    names = [
        id_doc_pairs.get(id, {}).get(keys.CLEAN_NAME)
        for id in id_group
        if "clone" not in id
    ]
    names = [n for n in names if n]
    return names


def set_match(self):
    """
    TODO iff same sizes
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

    common_tokens = dict()
    group_tokens = dict()
    self.inverted_index = collections.defaultdict(set)
    self.group_names = dict()

    logging.info("creating inverted index..")
    for id_group in tqdm(id_groups):
        names = get_names(id_group, self.id_doc_pairs)
        self.group_names[tuple(id_group)] = names

        token_sets = [filter_tokens(name) for name in names]
        if not token_sets:
            continue

        # update common_tokens
        commons = set.intersection(*token_sets)
        common_tokens[tuple(id_group)] = commons

        # update group_tokens
        all_tokens = set.union(*token_sets)
        group_tokens[tuple(id_group)] = all_tokens

        # update inverted_index
        for token in all_tokens:
            self.inverted_index[token].add(tuple(id_group))

    # filter empty sets
    self.common_tokens = {k: v for k, v in common_tokens.items() if v}
    self.group_tokens = {k: v for k, v in group_tokens.items() if v}

    unmatched_ids = set(self.id_doc_pairs.keys()).difference(self.connected_ids)
    single_names = [
        (doc_id, self.id_doc_pairs.get(doc_id, {}).get(keys.CLEAN_NAME))
        for doc_id in unmatched_ids
        if "clone" not in doc_id
    ]
    logging.info("matching singles..")
    # TODO match_singles is a bottleneck
    # this could be parallel but there are problems with multiprocessing code with class instances
    matched_names = [
        match_singles(self, doc_id, clean_name) for doc_id, clean_name in tqdm(single_names) if clean_name
    ]
    matched_names = [m for m in matched_names if m]

    logging.info("saving matched_names..")
    services.save_json("matched_names.json", matched_names)
