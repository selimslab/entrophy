import logging
import collections
from tqdm import tqdm

import services
import constants as keys


def index_groups(self, id_groups):
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
    self.size_index = collections.defaultdict(set)

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
        size_tuples = set(services.flatten(size_tuples))
        group[keys.DIGIT_UNIT_TUPLES] = size_tuples

        self.group_info[tuple(id_group)] = group
