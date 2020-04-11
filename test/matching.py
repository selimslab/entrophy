import constants as keys
import data_services
from services import json_util
from supermatch.main import create_matching
from test.test_logs.paths import get_paths

# from test.excel.excel import create_excel
import logging
import sys
from supermatch.syncer import strip_debug_fields, compare_and_sync

from test.test_links import *
from services import flatten


def run_matcher(name, links, links_of_products=None):
    query = {keys.LINK: {"$in": links}}
    docs_to_match = data_services.get_docs_to_match(query)

    full_skus = create_matching(
        docs_to_match=docs_to_match, links_of_products=links_of_products
    )

    basic_skus = strip_debug_fields(full_skus)
    compare_and_sync(basic_skus, is_test=True)

    paths = get_paths(name)
    # create_excel(cursor=docs, excel_path=paths.excel_path)
    json_util.save_json(paths.full_skus_path, full_skus)
    json_util.save_json(paths.basic_skus_path, basic_skus)


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    # run_matcher(name="süt", links=sut)
    run_matcher(name="cay", links=flatten(çaykur + sut))
