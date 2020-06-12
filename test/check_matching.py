import logging
import sys
import itertools

import services
import constants as keys
import data_services
import services
from supermatch.main import create_matching
from test import paths

from supermatch.syncer import Syncer
from supermatch import preprocess

from pprint import pprint

import pathlib

cwd = pathlib.Path.cwd()
input_dir = cwd / "in"
output_dir = cwd / "out"

raw_docs_path = input_dir / "raw_docs_path.json",
pairs_path = input_dir / "pairs.json",
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


def create_new_matching_from_existing_pairs():
    pairs = services.read_json(pairs_path)
    match_and_save(pairs)


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    logging.getLogger().setLevel(logging.DEBUG)
    create_new_matching_from_existing_pairs()
