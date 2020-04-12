import pandas as pd
import constants as keys


def create_excel(rows, path):
    items = list(rows)
    df = pd.DataFrame(items).fillna("")
    cols = [c for c in [ "product_id", "sku_id", "name", "link", "market",  "price", "size", "barcodes"] if c in df.columns]
    df = df[cols]
    df = df.sort_values(keys.PRODUCT_ID)
    df.to_excel(path, index=False)
    print("done")


if __name__ == "__main__":
    pass