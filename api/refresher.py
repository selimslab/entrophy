import data_services
from supermatch.main import create_matching
from supermatch.preprocess import pre_process
from supermatch.syncer import Syncer
import constants as keys
import sentry_sdk

sentry_sdk.init("https://39fd5a66307d47dcb3e9c37a8b709c44@sentry.io/5186400")


def create_new_matching():
    docs_to_match = data_services.get_docs_to_match(
        {keys.MARKET: {"$in": keys.MATCHING_MARKETS}}
    )
    pairs = pre_process(docs_to_match)
    skus: dict = create_matching(id_doc_pairs=pairs)
    syncer = Syncer(debug=False)
    syncer.sync_the_new_matching(skus)


if __name__ == "__main__":
    create_new_matching()
