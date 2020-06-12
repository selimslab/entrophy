from collections import defaultdict
import itertools

from tqdm import tqdm

import constants as keys


def exact_name_match(self):
    """
    TODO check here
    merge barcodeless items with a group
    if there is a member with the same name

    iff they have the same size
    """
    name_barcode_pairs = defaultdict(set)
    name_id_pairs = defaultdict(set)
    id_size_pairs = defaultdict(set)

    for doc_id, doc in self.id_doc_pairs.items():
        name = doc.get("clean_name")
        if not name:
            continue
        sorted_tokens = sorted(name.split())

        name_id_pairs[sorted_tokens].add(doc_id)

        barcodes = doc.get(keys.BARCODES, [])
        name_barcode_pairs[sorted_tokens].update(set(barcodes))

        id_size_pairs[doc_id] = doc.get(keys.DIGIT_UNIT_TUPLES, [])

    for key, barcodes in name_barcode_pairs.items():
        if len(barcodes) > 1:
            # this prevents connecting irrelevant groups
            continue

        doc_ids = name_id_pairs.get(key)

        single_doc_ids = [id for id in doc_ids if id not in self.connected_ids]

        if len(single_doc_ids) > 1:
            edges = itertools.combinations(single_doc_ids, 2)
            self.sku_graph.add_edges_from(edges)
            self.stages.update({**dict.fromkeys(single_doc_ids, "exact_name")})
            self.connected_ids.update(single_doc_ids)
