import logging
import sys
import itertools

import services
import constants as keys
import data_services
from services import json_util, excel, flatten
from supermatch.main import create_matching
from test.test_logs.paths import get_paths

from supermatch.syncer import Syncer
from supermatch import preprocess


def run_matcher(name: str, id_doc_pairs: dict, sync=False):
    paths = get_paths(name)

    full_skus = create_matching(id_doc_pairs=id_doc_pairs, debug=True)
    json_util.save_json(paths.full_skus, full_skus)

    excel.create_excel(full_skus, id_doc_pairs, paths.excel)

    json_util.save_json(paths.processed_docs, id_doc_pairs)

    syncer = Syncer(debug=True)
    basic_skus = syncer.strip_debug_fields(full_skus)
    json_util.save_json(paths.basic_skus, basic_skus)

    if sync:
        syncer.compare_and_sync(basic_skus)


def check_sync_only():
    paths = get_paths("end_to_end")
    full_skus = json_util.read_json(paths.full_skus)
    syncer = Syncer(debug=True)
    # syncer.sync_the_new_matching(full_skus)
    syncer.sync_the_new_matching(dict(itertools.islice(full_skus.items(), 1000)))


def check_partial():
    pairs = services.read_json("id_doc_pairs.json")
    pairs = dict(itertools.islice(pairs.items(), 100000, 120000))
    run_matcher(name="20k", sync=False, id_doc_pairs=pairs)


def check_query():
    links = json_util.read_json("links.json")
    query = {keys.LINK: {"$in": flatten(links)}}
    docs_to_match = data_services.get_docs_to_match(query)
    pairs = preprocess.create_id_doc_pairs(docs_to_match)
    run_matcher(name="query", sync=False, id_doc_pairs=pairs)


def check_all():
    pairs = services.read_json("id_doc_pairs.json")
    run_matcher(name="all_docs", sync=False, id_doc_pairs=pairs)


def refresh():
    docs_to_match = data_services.get_docs_to_match(
        {keys.MARKET: {"$in": keys.MATCHING_MARKETS}}
    )
    pairs = preprocess.pre_process(docs_to_match)
    services.save_json("latest_clean_pairs.json", pairs)


def check_latest():
    pairs = services.read_json("latest_clean_pairs.json")
    run_matcher(name="latest", sync=False, id_doc_pairs=pairs)


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    logging.getLogger().setLevel(logging.DEBUG)
