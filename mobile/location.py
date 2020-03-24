from pprint import pprint

import pandas as pd

from data_services.firebase.main import firestore_client


def read_location():
    loc = pd.read_excel("location.xlsx")
    df = pd.DataFrame(loc)
    locs = {}
    for index, row in df.iterrows():
        il = row["il"].lower()
        for col in df:
            if row[col] == 1:
                locs[il] = locs.get(il, []) + [col.lower()]

    pprint(locs)
    return locs


def push_location_to_fb():
    locs = read_location()

    for city, markets in locs.items():
        firestore_client.collection(u"location").document(city).set(
            {"markets": markets}
        )


def check_fb():

    docs = firestore_client.collection(u"location").stream()
    for doc in docs:
        city = doc.id
        markets = doc.to_dict().get("markets")
        print(city, markets)
        # firesync.db.collection(u"location").document(city).set({"markets": markets})


if __name__ == "__main__":
    check_fb()
