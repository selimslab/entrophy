from data_services import Elastic


def search_elastic_by_ids(ids: list) -> list:
    el = Elastic()
    # body = {"query": {"ids": {"values": ids}}}
    body = {
        "_source": {
            "includes": ["prices"]
        },
        "query": {"ids": {"values": ids}}
    }
    return el.search(body)


def search_elastic(query):
    el = Elastic()

    body = {
        "query": {
            "bool": {
                "must": {
                    "multi_match": {
                        "query": query,
                        "fields": ["name^2", "tags"],
                        "fuzziness": "AUTO",
                        "operator": "and",
                    }
                },
            }
        },
        "sort": ["_score"],
    }
    return el.search(body)


def search_barcode(barcodes: list):
    el = Elastic()

    body = {
        "query": {
            "bool": {
                "must": [{"match_all": {}}, ],
                "filter": [{"terms": {"barcodes": barcodes, }}, ],
            }
        }
    }

    return el.search(body)