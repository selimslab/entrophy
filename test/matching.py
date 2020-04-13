import logging
import sys
import itertools

import constants as keys
import data_services
from services import json_util, excel, flatten
from supermatch.main import create_matching
from test.test_logs.paths import get_paths

from supermatch.syncer import Syncer

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


def run_matcher(name, query, links_of_products=None):
    paths = get_paths(name)

    docs_to_match = data_services.get_docs_to_match(query)

    full_skus = create_matching(
        docs_to_match=docs_to_match, links_of_products=links_of_products
    )
    json_util.save_json(paths.full_skus, full_skus)

    docs = [sku.get("docs") for sku in full_skus.values()]
    docs = list(itertools.chain.from_iterable(docs))
    json_util.save_json(paths.docs, docs)

    excel.create_excel(docs, paths.excel)

    syncer = Syncer(is_test=True)

    basic_skus = syncer.strip_debug_fields(full_skus)
    json_util.save_json(paths.basic_skus, basic_skus)

    syncer.compare_and_sync(basic_skus)


def check_matching():
    links = json_util.read_json("links.json")
    query = {keys.LINK: {"$in": flatten(links)}}
    # query = {}
    run_matcher(name="basic", query=query)


if __name__ == "__main__":
    paths = get_paths("end_to_end")
    full_skus = json_util.read_json(paths.full_skus)
    syncer = Syncer(is_test=True)
    syncer.sync_the_new_matching(dict(itertools.islice(full_skus.items(), 2))
)
