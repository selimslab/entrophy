import constants as keys


def get_raw_docs_with_markets_and_cats_only():
    from data_services.mongo.collections import items_collection

    cursor = items_collection.find(
        {
            keys.MARKET: {"$exists": True},
            keys.CATEGORIES: {"$exists": True},
            keys.MARKETS: {"$nin": [keys.TRENDYOL, keys.WATSONS]},
        },
        {keys.MARKET: 1, keys.CATEGORIES: 1, keys.BRAND: 1, "_id": 0},
    )
    return cursor


def ask_a_question():
    from data_services.mongo.collections import items_collection
    from pprint import pprint

    print(items_collection.count_documents({"color": {"$exists": True}}))
    cursor = {}
    for doc in cursor:
        pprint(doc)


if __name__ == "__main__":
    ask_a_question()
