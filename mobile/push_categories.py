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
