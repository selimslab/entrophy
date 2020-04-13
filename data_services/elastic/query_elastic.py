from .main import elastic


def search_elastic(query):
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
    return elastic.search(body)


def search_barcode(barcodes: list):
    body = {
        "query": {
            "bool": {
                "must": [{"match_all": {}},],
                "filter": [{"terms": {"barcodes": barcodes,}},],
            }
        }
    }

    return elastic.search(body)


if __name__ == "__main__":
    pass
