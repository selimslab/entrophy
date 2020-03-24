import pandas as pd

import constants as keys
import data_services.mongo.collections as collections


def create_df(cursor, projection):
    items = list(cursor)
    df = pd.DataFrame(items).fillna("")

    print("preparing the data frame..")
    cols = [c for c in projection.keys() if c in df.columns]
    df = df[cols]

    print("sorting..")
    # df[keys.PRODUCT_ID] = pd.to_numeric(df[keys.PRODUCT_ID], errors="coerce")
    df[keys.PRODUCT_ID] = df[keys.PRODUCT_ID].astype(str)
    df = df.sort_values(keys.PRODUCT_ID)

    return df


def create_excel(query=None, projection=None, excel_path=None, cursor=None):
    if query is None:
        query = {}

    if projection is None:
        projection = {
            keys.LINK: 1,
            keys.MARKET: 1,
            keys.NAME: 1,
            keys.SIZE: 1,
            keys.PRICE: 1,
            keys.BARCODES: 1,
            keys.PROMOTED: 1,
            keys.VARIANTS: 1,
            keys.VARIANT_NAME: 1,
            keys.SKU_ID: 1,
            keys.PRODUCT_ID: 1,
        }

    if cursor is None:
        print("collecting the data..")
        cursor = collections.items_collection.find(query, projection)

    if excel_path is None:
        excel_path = "groups.xlsx"

    df = create_df(cursor, projection)
    print("exporting to excel..")
    df.to_excel(excel_path, index=False)
    print("done.")


if __name__ == "__main__":
    create_excel()
