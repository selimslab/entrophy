from data_services.firebase.main import firestore_client

from mobile.cat import raw_cats


def push_cats():
    tree = dict()

    for doc in raw_cats:
        cat = doc.get("cat")
        tree[cat] = tree.get(cat, []) + [
            {"name": doc.get("subcat"), "kw": doc.get("kw"), "src": doc.get("src")}
        ]

    icons = {
        "Kozmetik": "cosmetics.svg",
        "Kişisel Bakım": "kisisel bakim.svg",
        "Gıda": "gida.svg",
        "Ev Bakımı": "ev bakim.svg",
        "Bebek": "baby.svg",
        "Pet": "pet.svg",
    }

    order = ["Kişisel Bakım", "Kozmetik", "Ev Bakımı", "Gıda", "Bebek", "Pet"]

    cats = []
    for cat in order:
        new_cat = {}
        new_cat["name"] = cat
        new_cat["subcategories"] = tree[cat]
        new_cat["icon"] = (
                "https://narmoni.s3.eu-central-1.amazonaws.com/market_logos/icons/"
                + icons.get(cat)
        )
        cats.append(new_cat)

    return cats


def sync_cats():
    from pprint import pprint

    cats = push_cats()
    pprint(cats)

    firestore_client.collection(u"config").document(u"categories").set({"all": cats})


def sync_search():
    search_keyword = {
        "from": 0,
        "size": 30,
        "_source": {
            "excludes": [
                "tags",
                "product_ids_count",
                "sku_ids_count",
                "links",
                "barcodes",
            ]
        },
        "query": {
            "bool": {
                "must": {
                    "multi_match": {
                        "query": "milka",
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
            "excludes": ["tags", "product_ids_count", "sku_ids_count", "links"]
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
            "excludes": ["tags", "product_ids_count", "sku_ids_count", "links"]
        },
        "query": {
            "bool": {
                "must": [{"match_all": {}}],
                "filter": [
                    {"ids": {"values": ["5d7bdfa6525e36c343df0d8c", "5d7bdfa6525e36c343df0e4e"]
                             }
                     }
                ]
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
