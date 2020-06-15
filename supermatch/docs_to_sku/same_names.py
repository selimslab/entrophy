from collections import defaultdict
import itertools
import logging

from tqdm import tqdm

import constants as keys


def exact_name_match(self):
    """match items with the the same name

    iff they have the same size
    """
    name_barcode_pairs = defaultdict(set)
    name_id_pairs = defaultdict(set)
    id_size_pairs = defaultdict(set)

    for doc_id, doc in self.id_doc_pairs.items():
        name = doc.get(keys.CLEAN_NAME)
        if not name:
            continue
        sorted_tokens = tuple(sorted(name.split()))
        name_id_pairs[sorted_tokens].add(doc_id)

        barcodes = doc.get(keys.BARCODES, [])
        name_barcode_pairs[sorted_tokens].update(set(barcodes))

        id_size_pairs[doc_id] = doc.get(keys.DIGIT_UNIT_TUPLES, [])

    logging.info("looking for docs with the same names..")
    # only 1 barcode per sku is allowed
    for name, barcodes in tqdm(name_barcode_pairs.items()):
        if len(barcodes) > 1:
            # this prevents connecting irrelevant groups
            continue

        doc_ids = name_id_pairs.get(name)

        single_doc_ids = [id for id in doc_ids if id not in self.connected_ids]

        if len(single_doc_ids) <= 1:
            continue

        edges = itertools.combinations(single_doc_ids, 2)
        # chec edges for size
        for edge in edges:
            size1, size2 = id_size_pairs.get(edge[0]), id_size_pairs.get(edge[1])
            if size1 and size2 and not set(size1).intersection(size2):
                continue

            self.sku_graph.add_edges_from(edges)
            self.stages.update({**dict.fromkeys(single_doc_ids, "exact_name")})
            self.connected_ids.update(single_doc_ids)
