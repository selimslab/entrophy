from .main import elastic


def search_elastic_by_ids(ids: list, source) -> list:
    body = {"_source": source, "query": {"ids": {"values": ids}}}
    return elastic.search(body)


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
                "must": [{"match_all": {}}, ],
                "filter": [{"terms": {"barcodes": barcodes, }}, ],
            }
        }
    }

    return elastic.search(body)


if __name__ == "__main__":
    search_elastic_by_ids(
        [
            "5e54cfc2d1e09b159549e7e3",
            "5e11bd9c1b07cf6bf3b913dd",
            "5d7bdfa6525e36c343df0d8c",
            "5d7bdfa6525e36c343df0e4e",
        ]
    )
