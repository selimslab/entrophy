import logging
import sys
import itertools
import pathlib

import constants as keys
import data_services
import services

from supermatch.main import create_matching
from supermatch import preprocess

cwd = pathlib.Path.cwd()
input_dir = cwd / "in"
output_dir = cwd / "out"

raw_docs_path = input_dir / "raw_docs_path.json"
pairs_path = input_dir / "pairs.json"
skus_path = output_dir / "skus.json"


def match_and_save(pairs):
    skus: dict = create_matching(id_doc_pairs=pairs)
    services.save_json(skus_path, skus)


def create_new_matching_from_query():
    links = services.read_json("test_logs/old/links.json")
    query = {keys.LINK: {"$in": services.flatten(links)}}
    docs_to_match = data_services.get_docs_to_match(query)
    pairs = preprocess.get_clean_id_doc_pairs(docs_to_match)
    services.save_json(pairs_path, pairs)
    match_and_save(pairs)


def create_new_matching_from_scratch():
    docs_to_match = data_services.get_docs_to_match(
        {keys.MARKET: {"$in": keys.MATCHING_MARKETS}}
    )
    pairs = preprocess.get_clean_id_doc_pairs(docs_to_match)
    services.save_json(pairs_path, pairs)
    match_and_save(pairs)


def create_new_matching_from_existing_pairs(start: int = None, end: int = None):
    pairs = services.read_json(pairs_path)
    if start is None:
        start = 0
    if end is None:
        end = len(pairs)
    slice = itertools.islice(pairs.items(), start, end)
    match_and_save(dict(slice))


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    logging.getLogger().setLevel(logging.DEBUG)
    create_new_matching_from_existing_pairs(10000, 110000)
