import collections
import random
import typing

import constants as keys


def get_sku_id_doc_ids_pairs(
    groups_of_doc_ids: typing.Iterator, filtered_id_doc_pairs: dict
) -> dict:
    """
    Use the most_common SKU_ID if present, else choose a new id
    """
    sku_id_doc_ids_pairs = dict()

    for list_of_doc_ids in groups_of_doc_ids:
        filtered_list_of_doc_ids = [id for id in list_of_doc_ids if "clone" not in id]
        possible_sku_ids = list()
        for doc_id in filtered_list_of_doc_ids:
            doc = filtered_id_doc_pairs.get(doc_id, {})
            sku_id = doc.get(keys.SKU_ID)
            if sku_id and "clone" not in sku_id and sku_id not in sku_id_doc_ids_pairs:
                possible_sku_ids.append(sku_id)

        if possible_sku_ids:
            sku_id = collections.Counter(possible_sku_ids).most_common(1)[0][0]
        else:
            candidate_ids = [
                doc_id
                for doc_id in filtered_list_of_doc_ids
                if doc_id not in sku_id_doc_ids_pairs
            ]
            if candidate_ids:
                sku_id = sorted(candidate_ids)[0]
            else:
                sku_id = sorted(list_of_doc_ids)[0] + str(random.randint(1, 100))
                while sku_id in sku_id_doc_ids_pairs:
                    sku_id = sorted(list_of_doc_ids)[0] + str(random.randint(1, 100))

        sku_id_doc_ids_pairs[sku_id] = list_of_doc_ids

    return sku_id_doc_ids_pairs
