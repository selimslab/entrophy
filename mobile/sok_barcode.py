import pandas as pd

import constants as keys


def doc_generator():
    loc = pd.read_excel("y.xlsx")
    df = pd.DataFrame(loc)
    for index, row in df.iterrows():
        doc = {keys.LINK: row.get("link"), keys.BARCODES: [str(row["code"])]}
        yield doc


def push():
    to_be_updated = [doc for doc in doc_generator()]
    print(to_be_updated)
