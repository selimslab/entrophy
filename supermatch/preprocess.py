from typing import Iterator

from tqdm import tqdm

import constants as keys
import logging


def get_clean_id_doc_pairs(docs_to_match: Iterator) -> dict:
    pairs = create_id_doc_pairs(docs_to_match)
    pairs = clean_links(pairs)
    pairs = clone_docs_with_multiple_barcodes(pairs)
    return pairs


def create_id_doc_pairs(docs_to_match: Iterator) -> dict:
    logging.info("create_id_doc_pairs..")
    return {
        str(doc.pop("_id")): doc
        for doc in tqdm(docs_to_match)
        if doc and keys.LINK in doc
    }


def clone_docs_with_multiple_barcodes(pairs):
    clones = {}
    cloned_doc_ids = set()
    logging.info("clone_docs_with_multiple_barcodes..")
    for doc_id, doc in tqdm(pairs.items()):
        barcodes = doc.get(keys.BARCODES, [])
        if barcodes and len(barcodes) > 1:
            for i, barcode in enumerate(barcodes):
                copy_id = doc_id + "+clone" + str(i)
                copy_of_doc = doc.copy()
                copy_of_doc[keys.BARCODES] = [barcode]
                clones[copy_id] = copy_of_doc
            cloned_doc_ids.add(doc_id)

    pairs = {
        doc_id: doc
        for doc_id, doc in tqdm(pairs.items())
        if doc_id not in cloned_doc_ids
    }
    logging.info(
        f"{len(cloned_doc_ids)} cloned, {len(clones)} clones, {len(pairs)} pairs"
    )
    pairs.update(clones)
    return pairs


def clean_links(pairs):
    logging.info("clean_links..")
    for doc_id, doc in tqdm(pairs.items()):
        link = doc.get(keys.LINK)
        if link[-1] == "/":
            doc[keys.LINK] = link[:-1]
    return pairs
