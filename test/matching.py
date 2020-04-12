import logging
import sys
import itertools

import constants as keys
import data_services
from services import json_util, excel, flatten
from supermatch.main import create_matching
from test.test_logs.paths import get_paths

from supermatch.syncer import strip_debug_fields, compare_and_sync


def run_matcher(name, links, links_of_products=None):
    paths = get_paths(name)

    query = {keys.LINK: {"$in": links}}
    docs_to_match = data_services.get_docs_to_match(query)

    full_skus = create_matching(
        docs_to_match=docs_to_match, links_of_products=links_of_products
    )

    docs = [sku.get("docs") for sku in full_skus.values()]
    docs = list(itertools.chain.from_iterable(docs))
    json_util.save_json(paths.docs, docs)
    excel.create_excel(docs, paths.excel)

    basic_skus = strip_debug_fields(full_skus)
    # compare_and_sync(basic_skus, is_test=True)

    json_util.save_json(paths.full_skus, full_skus)
    json_util.save_json(paths.basic_skus, basic_skus)


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    links = json_util.read_json("links.json")
    # run_matcher(name="süt", links=sut)
    run_matcher(name="end_to_end", links=flatten(links))
