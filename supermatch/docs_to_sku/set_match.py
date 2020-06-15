import logging
import operator
import itertools
import collections
from tqdm import tqdm
from typing import Set, Union, List

import services
import constants as keys
from .index_groups import Indexer


def search_groups_to_connect(
        inverted_index: dict, group_info: dict, name: str, sizes_in_name: set
) -> Union[Set[tuple], None]:
    token_set = set(name.split())
    # eligible groups include all tokens of the name
    # which groups has the tokens of this name
    candidate_groups = [inverted_index.get(token, []) for token in token_set]

    # for every token, what are the set of ids?
    candidate_groups = [set(itertools.chain(group)) for group in candidate_groups]
    # which groups has all tokens of the name,
    # a group  must cover all tokens of the single name
    candidate_groups = set.intersection(*candidate_groups)
    matches = set()

    for id_group in candidate_groups:
        group = group_info.get(id_group, {})
        group_common: set = group.get("common_tokens", set())
        group_sizes: set = group.get(keys.DIGIT_UNIT_TUPLES, set)

        # they should be same size
        if sizes_in_name and (not group_sizes.intersection(sizes_in_name)):
            continue

        # single name must cover all common tokens of the group
        if not token_set.issuperset(group_common):
            continue

        # first common, if commons same, difference
        matches.add((len(group_common), id_group))

    return matches


def select_a_match(matches: Set[tuple])->tuple:
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


def set_match_generator_for_docs(self):
    """build inverted_index and group_info for doc pairs"""
    id_groups: list = self.get_connected_groups()
    indexer = Indexer()
    logging.info("creating group_info and inverted index..")
    for id_group in tqdm(id_groups):
        docs = [
            self.id_doc_pairs.get(doc_id, {})
            for doc_id in id_group
            if "clone" not in doc_id
        ]

        group_key = tuple(id_group)
        indexer.index(docs, group_key)

    logging.info("matching singles..")
    # this could be parallel but there are problems with multiprocessing code with class instances
    for doc_id, doc in tqdm(self.single_doc_generator()):
        clean_name = doc.get(keys.CLEAN_NAME)
        if not clean_name:
            continue
        sizes_in_name = doc.get(keys.DIGIT_UNIT_TUPLES, [])
        # a single name could be matched to multiple groups
        matches = search_groups_to_connect(indexer.inverted_index, indexer.group_info, clean_name, set(sizes_in_name))

        if not matches:
            continue

        match: tuple = select_a_match(matches)
        _, group_to_connect = match

        if group_to_connect:
            # connect to single doc to the first element of id group,
            # since the group is all connected, any member will do
            nodes_to_connect = [(doc_id, group_to_connect[0])]
            yield nodes_to_connect


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
    for nodes_to_connect in set_match_generator_for_docs(self):
        self.sku_graph.add_edges_from(nodes_to_connect)
        doc_id, _ = nodes_to_connect
        self.connected_ids.add(doc_id)
        self.stages[doc_id] = "set_match"
