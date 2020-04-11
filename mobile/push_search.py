from data_services.firebase.main import firestore_client


def sync_search():

    search_keyword = {
        "from": 0,
        "size": 24,
        "_source": {
            "excludes": [
                "tags",
                "product_ids_count",
                "sku_ids_count",
                "links",
                "barcodes"
            ]
        },
        "query": {
            "bool": {
                "must": {
                    "multi_match": {
                        "query": "",
                        "fields": ["name^2", "tags"],
                        "fuzziness": "AUTO",
                        "operator": "and",
                    }
                },
                "filter": {"terms": {"markets": []}},
            },
        },
        "sort": ["_score"],
    }

    search_barcode = {
        "from": 0,
        "size": 10,
        "_source": {
            "excludes": ["tags"]
        },
        "query": {
            "bool": {
                "must": [{"match_all": {}}, ],
                "filter": [
                    {"terms": {"barcodes": ["8690506390907", "1825470015283"], }},
                ],
            }
        },
    }

    search_by_id = {
        "_source": {
            "includes": ["prices",""]
        },
        "query": {
            "ids": {
                "values":
                    []
            }
        }
    }
    """
    {"best_price": {"order": "asc"}},
    {"market_count": {"order": "desc"}}, 
    """

    url = "https://search-narmoni-sby3slciocpfo5f3ubqhplod7u.eu-central-1.es.amazonaws.com/products/_search"
    firestore_client.collection(u"config").document(u"search").set(
        {"url": url, "query": search_keyword, "barcode_search": search_barcode, "search_by_id": search_by_id}
    )


if __name__ == "__main__":
    sync_search()
