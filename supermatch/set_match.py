import logging
import operator
import itertools
import collections
from tqdm import tqdm
from typing import List

import services
import constants as keys


def get_matches(self, name: str) -> List[tuple]:
    token_set = set(name.split())
    # eligible groups include all tokens of the name
    candidate_groups = [self.inverted_index.get(token, []) for token in token_set]
    candidate_groups = set(itertools.chain(*candidate_groups))
    if not candidate_groups:
        return []

    matches = set()

    for id_group in candidate_groups:
        # TODO iff same sizes

        group = self.group_info.get(id_group, {})
        group_tokens = group.get("group_tokens", set())
        group_common = group.get("common_tokens", set())

        # single name must cover all common tokens of the group
        if not token_set.issuperset(group_common):
            continue

        # the group  must cover all tokens of the single name
        if not group_tokens.issuperset(token_set):
            continue

        ### diff_size = len(group_tokens.difference(token_set))

        # first common, if commons same, difference
        matches.add((len(group_common), id_group))

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


def search_a_group_to_connect(self, name):
    """ connect single name to a group """

    # a single name could be matched to multiple groups
    matches = get_matches(self, name)

    if not matches:
        return

    match = select_a_match(matches)
    _, id_group = match

    return id_group


def prep(self, id_groups):
    """
    add group_info and inverted_index to the self

    group_info : {
        (member ids, ..) : {
            tokens : set()
            common_tokens: set()
            DIGIT_UNIT_TUPLES: [ (75, "ml"), .. ]
        }
    }


    inverted_index : {
        token : set( (member_ids.. ), ..)
    }
    """
    logging.info("creating group_info and inverted index..")

    self.group_info = collections.defaultdict(dict)
    self.inverted_index = collections.defaultdict(set)

    for id_group in tqdm(id_groups):
        group = dict()
        docs = [self.id_doc_pairs.get(doc_id, {}) for doc_id in id_group if "clone" not in doc_id]

        names = [
            doc.get(keys.CLEAN_NAME)
            for doc in docs
        ]
        names = [n for n in names if n]

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


def add_edges_by_set_match(self, single_names):
    logging.info("matching singles..")
    # this could be parallel but there are problems with multiprocessing code with class instances
    for doc_id, clean_name in tqdm(single_names):
        if clean_name:
            group_to_connect = search_a_group_to_connect(self, clean_name)
            if group_to_connect:
                # connect to single doc to the first element of id group,
                # since the group is all connected, any member will do
                nodes_to_connect = [(doc_id, group_to_connect[0])]
                self.sku_graph.add_edges_from(nodes_to_connect)
                self.connected_ids.add(doc_id)
                self.stages[doc_id] = "set_match"


def get_single_names(self):
    unmatched_ids = set(self.id_doc_pairs.keys()).difference(self.connected_ids)
    single_names = [
        (doc_id, self.id_doc_pairs.get(doc_id, {}).get(keys.CLEAN_NAME))
        for doc_id in unmatched_ids
        if "clone" not in doc_id
    ]
    return single_names


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
    #
    prep(self, id_groups)
    single_names = get_single_names(self)
    add_edges_by_set_match(self, single_names)
