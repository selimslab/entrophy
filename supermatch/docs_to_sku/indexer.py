import logging
import collections
import itertools
from typing import List, Union, Set

from tqdm import tqdm

import services
import constants as keys


class Indexer:
    def __init__(self):
        """
        group_info : {
            key : {
                tokens : set()
                common_tokens: set()
                DIGIT_UNIT_TUPLES: [ (75, "ml"), .. ],
            }
        }

        key can be a single id or a tuple of ids
        (member ids, ..)


        inverted_index : {
            token : set( (member_ids.. ), ..)
        }
        """
        self.group_info = collections.defaultdict(dict)
        self.inverted_index = collections.defaultdict(set)

    def index_skus(self, sku, sku_id):
        group = dict()

        names = sku.get(keys.CLEAN_NAMES, [])

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
            self.inverted_index[token].add(sku_id)

        size_tuples = sku.get(keys.DIGIT_UNIT_TUPLES, [])
        size_tuples = set(services.flatten(size_tuples))
        group[keys.DIGIT_UNIT_TUPLES] = size_tuples

        self.group_info[sku_id] = group

    def index_docs(self, docs: List[dict], group_key: Union[tuple, str, int]):
        group = dict()

        names = [doc.get(keys.CLEAN_NAME) for doc in docs]
        names = [n for n in names if n]
        if not names:
            return

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
            self.inverted_index[token].add(group_key)

        size_tuples = [doc.get(keys.DIGIT_UNIT_TUPLES) for doc in docs]
        size_tuples = set(services.flatten(size_tuples))
        group[keys.DIGIT_UNIT_TUPLES] = size_tuples

        self.group_info[group_key] = group

    def search_skus_to_connect(self, sku, sku_id):

        sku_index = self.group_info.get(sku_id, {})
        token_set = sku_index.get("tokens")

        all_sku_ids_for_this_tokens = [
            self.inverted_index.get(token, []) for token in token_set
        ]
        # for every token, what are the set of ids?
        candidate_sku_ids = [
            set(itertools.chain(group)) for group in all_sku_ids_for_this_tokens
        ]
        # which groups has all tokens of the name,
        # a group  must cover all tokens of the single name
        candidate_sku_ids = set.intersection(*candidate_sku_ids)

        matches = dict()
        sizes_in_name = sku.get(keys.DIGIT_UNIT_TUPLES, set())
        for sid in candidate_sku_ids:
            group = self.group_info.get(sid, {})
            group_common: set = group.get("common_tokens", set())
            group_sizes: set = group.get(keys.DIGIT_UNIT_TUPLES, set())

            # they should be same size
            if sizes_in_name and (not group_sizes.intersection(sizes_in_name)):
                continue

            # single name must cover all common tokens of the group
            if not token_set.issuperset(group_common):
                continue

            matches[sid] = len(group_common)

        return matches

    def search_doc_groups_to_connect(self, name: str, sizes_in_name: set) -> dict:
        token_set = set(name.split())
        # eligible groups include all tokens of the name
        # which groups has the tokens of this name
        candidate_keys = [self.inverted_index.get(token, []) for token in token_set]

        # for every token, what are the set of ids?
        candidate_keys = [set(itertools.chain(group)) for group in candidate_keys]
        # which groups has all tokens of the name,
        # a group  must cover all tokens of the single name
        candidate_keys = set.intersection(*candidate_keys)
        # could be replaced with a dict key: count
        matches = dict()

        for key in candidate_keys:
            group = self.group_info.get(key, {})
            group_common: set = group.get("common_tokens", set())
            group_sizes: set = group.get(keys.DIGIT_UNIT_TUPLES, set())

            # they should be same size
            if sizes_in_name and (not group_sizes.intersection(sizes_in_name)):
                continue

            # single name must cover all common tokens of the group
            if not token_set.issuperset(group_common):
                continue

            matches[key] = len(group_common)

        return matches
