import data_services
from supermatch.main import create_matching
from supermatch.syncer import Syncer
import api.sentry
import constants as keys


def create_new_matching():
    docs_to_match = data_services.get_docs_to_match({keys.MARKET: {"$in": keys.MATCHING_MARKETS}})
    links_of_products: set = data_services.get_links_of_products()
    skus: dict = create_matching(
        docs_to_match=docs_to_match, links_of_products=links_of_products, debug=False
    )
    syncer = Syncer(is_test=False)
    syncer.sync_the_new_matching(skus)


if __name__ == "__main__":
    create_new_matching()
