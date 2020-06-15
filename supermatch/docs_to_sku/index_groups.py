import logging
import collections
from tqdm import tqdm
from typing import List

import services
import constants as keys


class Indexer:
    def __init__(self):
        """
        group_info : {
            (member ids, ..) : {
                tokens : set()
                common_tokens: set()
                DIGIT_UNIT_TUPLES: [ (75, "ml"), .. ],
            }
        }


        inverted_index : {
            token : set( (member_ids.. ), ..)
        }
        """
        self.group_info = collections.defaultdict(dict)
        self.inverted_index = collections.defaultdict(set)

    def index(self, docs: List[dict], group_key: tuple):
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
