import pandas as pd
import constants as keys
import logging

from tqdm import tqdm


def create_excel(rows: list, path, colnames: list):
    print("filtering rows..")
    items = [{k: v for k, v in doc.items() if k in set(colnames)} for doc in tqdm(rows)]

    print("rows to df..")
    df = pd.DataFrame(items).fillna("")

    print("filtering columns..")
    cols = [c for c in colnames if c in df.columns]
    df = df[cols]

    print("sorting..")
    df = df.sort_values(keys.SKU_ID)

    print("df to excel..")
    df.to_excel(path, index=False)
    print("done")


if __name__ == "__main__":
    ...
