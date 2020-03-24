import data_services
import supermatch
from api.report_decorator import report_decorator
from data_models.matching import MatchingMechanism
from supersync.syncer import sync_the_new_matching


@report_decorator
def create_new_matching():
    docs_to_match = data_services.get_docs_to_match({})
    links_of_products: set = data_services.get_links_of_products()
    matching_collection = supermatch.create_matching(
        docs_to_match=docs_to_match, links_of_products=links_of_products
    )
    sync_the_new_matching(matching_collection)


if __name__ == "__main__":
    create_new_matching()
