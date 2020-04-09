from itertools import combinations

from fuzzywuzzy import fuzz
from tqdm import tqdm

import constants as keys
import data_services.mongo.collections as collections


class NodeSimilarity:
    @staticmethod
    def add_similarity(neighbor_update, id_sku_pairs):
        if neighbor_update:
            id_neighbor_pairs = NodeSimilarity.get_id_neighbor_pairs(id_sku_pairs)
            if id_neighbor_pairs:
                collections.subs_collection.delete_one()
                collections.subs_collection.insert_one(id_neighbor_pairs)
        else:
            id_neighbor_pairs = collections.subs_collection.find_one()

        for sku_id, subs in id_neighbor_pairs.items():
            if sku_id in id_sku_pairs:
                id_sku_pairs[sku_id][keys.SUBS] = subs

        return id_sku_pairs

    @staticmethod
    def get_pairs_to_compare(id_token_pairs):
        """
        if a token is present in more than 1 places,
        it means a token intersection for this SKU

        :param id_token_pairs:
        :return:
        """
        token_sku_id_pairs = dict()
        for sku_id, tokens in id_token_pairs.items():
            for token in tokens:
                token_sku_id_pairs[token] = token_sku_id_pairs.get(token, []) + [sku_id]

        pairs_to_compare = set()
        for token, sku_ids in token_sku_id_pairs.items():
            id_combinations = combinations(sku_ids, 2)
            for (id1, id2) in id_combinations:
                if (id2, id1) not in pairs_to_compare:
                    pairs_to_compare.add((id1, id2))

        return pairs_to_compare

    @staticmethod
    def get_id_neighbor_pairs(id_sku_pairs: dict):
        id_neighbor_pairs = dict()

        id_token_pairs = dict()
        id_tags_pairs = dict()

        for sku_id, sku in id_sku_pairs.items():
            id_token_pairs[sku_id] = set(sku.get(keys.MOST_COMMON_TOKENS, []))
            id_tags_pairs[sku_id] = sku.get(keys.TAGS)

        pairs_to_compare = NodeSimilarity.get_pairs_to_compare(id_token_pairs)
        print(len(pairs_to_compare), "pairs_to_compare")

        for (id1, id2) in tqdm(pairs_to_compare):
            tags1, tags2 = id_tags_pairs.get(id1), id_tags_pairs.get(id2)
            score = fuzz.ratio(tags1, tags2)
            if score >= 80:
                id_neighbor_pairs[id1] = id_neighbor_pairs.get(id1, []) + [id2]

        return id_neighbor_pairs


if __name__ == "__main__":
    pass
