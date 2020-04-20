from typing import Iterator

from tqdm import tqdm

import constants as keys
import logging

def create_id_doc_pairs(docs_to_match: Iterator) -> dict:
    id_doc_pairs = dict()
    for doc in tqdm(docs_to_match):
        if not doc:
            continue
        link = doc.get(keys.LINK)
        if not link:
            continue

        doc_id = str(doc.pop("_id"))

        if link[-1] == "/":
            link = link[:-1]
            doc[keys.LINK] = link

        barcodes = doc.get(keys.BARCODES, [])
        # clone_docs_with_multiple_barcodes
        if barcodes and len(barcodes) > 1:
            logging.info(f"cloning {barcodes}, {doc}")
            for i, barcode in enumerate(barcodes):
                copy_id = doc_id + "+clone" + str(i)
                copy_of_doc = doc.copy()
                copy_of_doc[keys.BARCODES] = [barcode]
                id_doc_pairs[copy_id] = copy_of_doc
        else:
            id_doc_pairs[doc_id] = doc

    return id_doc_pairs
