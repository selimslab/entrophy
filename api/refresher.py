import data_services

from supermatch.main import create_matching
from supermatch.prep.preprocess import get_clean_id_doc_pairs
from supermatch.syncer import Syncer

from enricher.main import add_brand_sub_brand_subcat_to_skus

import constants as keys
import sentry_sdk

sentry_sdk.init("https://39fd5a66307d47dcb3e9c37a8b709c44@sentry.io/5186400")


def create_new_matching():
    # prep
    docs_to_match = data_services.get_docs_to_match(
        {keys.MARKET: {"$in": keys.MATCHING_MARKETS}}
    )
    pairs = get_clean_id_doc_pairs(docs_to_match)

    # match
    skus: dict = create_matching(id_doc_pairs=pairs)

    # enrich
    skus, _ = add_brand_sub_brand_subcat_to_skus(skus)

    # sync
    syncer = Syncer(debug=False)
    syncer.sync_the_new_matching(skus)


if __name__ == "__main__":
    create_new_matching()
