import pandas as pd
import constants as keys
import logging

from tqdm import tqdm

colnames = [
    "product_id",
    "sku_id",
    "link",
    "name",
    # "clean_name",
    "digits",
    "unit",
    # "size",
    "market",
    # "price",
    "barcodes",
    # keys.OUT_OF_STOCK,
    # keys.VARIANT_NAME,
    # "stage",
    "brand",
    "our_brand",
    keys.CATEGORIES,
    keys.SUBCAT,
]


def filter_excel_rows(doc):
    return {k: v for k, v in doc.items() if k in set(colnames)}


def prepare_excel(full_skus, id_doc_pairs):
    rows = list()

    for sku in full_skus.values():
        sku_id = sku.get(keys.SKU_ID)
        product_id = sku.get(keys.PRODUCT_ID)
        for doc_id in sku.get("doc_ids"):
            doc = id_doc_pairs.get(doc_id, {})
            doc[keys.SKU_ID] = sku_id
            doc[keys.PRODUCT_ID] = product_id
            doc = filter_excel_rows(doc)
            rows.append(doc)

    return rows


def create_excel(rows: list, path):
    print("creating excel..")
    items = [filter_excel_rows(doc) for doc in tqdm(rows)]
    df = pd.DataFrame(items).fillna("")
    cols = [c for c in colnames if c in df.columns]
    df = df[cols]
    df = df.sort_values(keys.SKU_ID)
    df.to_excel(path, index=False)
    print("done")


if __name__ == "__main__":
    ...
