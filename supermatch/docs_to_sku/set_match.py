import logging
import operator
import itertools
import collections
from tqdm import tqdm
from typing import Set, Union, List

import services
import constants as keys
from .index_groups import Indexer


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
        matches: dict = indexer.search_groups_to_connect(clean_name, set(sizes_in_name))

        if matches:
            key_to_connect = services.get_most_frequent_key(matches)
            # connect to single doc to the first element of id group,
            # since the group is all connected, any member will do
            yield doc_id, key_to_connect


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
    for doc_id, key_to_connect  in set_match_generator_for_docs(self):
        self.sku_graph.add_edges_from([(doc_id, key_to_connect)])
        self.connected_ids.add(doc_id)
        self.stages[doc_id] = "set_match"
