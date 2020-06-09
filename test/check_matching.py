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
logs_dir = cwd / "logs"


def check_query():
    links = services.read_json("test_logs/old/links.json")
    query = {keys.LINK: {"$in": services.flatten(links)}}
    docs_to_match = data_services.get_docs_to_match(query)
    pairs = preprocess.create_id_doc_pairs(docs_to_match)

    services.save_json(logs_dir / "pairs.json", pairs)
    skus: dict = create_matching(id_doc_pairs=pairs)
    services.save_json(logs_dir / "skus.json", skus)


def create_new_matching_from_scratch():
    docs_to_match = data_services.get_docs_to_match(
        {keys.MARKET: {"$in": keys.MATCHING_MARKETS}}
    )
    pairs = preprocess.get_clean_id_doc_pairs(docs_to_match)
    services.save_json(logs_dir / "pairs.json", pairs)
    skus: dict = create_matching(id_doc_pairs=pairs)
    services.save_json(logs_dir / "skus.json", skus)


def create_new_matching_from_existing_pairs():
    pairs = services.read_json(logs_dir / "pairs.json")
    skus: dict = create_matching(id_doc_pairs=pairs)
    services.save_json(logs_dir / "skus.json", skus)


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    logging.getLogger().setLevel(logging.DEBUG)
    create_new_matching_from_existing_pairs()
    # why ty is not included in matching ??
    # because their newly issued sku and pid s are not added to pairs
