import pandas as pd
import constants as keys


def create_excel(full_skus, id_doc_pairs, path):
    rows = list()
    colnames = [
        "product_id",
        "sku_id",
        "link",
        "name",
        "market",
        "price",
        "size",
        "barcodes",
        "variants",
        keys.VARIANT_NAME
    ]
    for sku in full_skus.values():
        sku_id = sku.get(keys.SKU_ID)
        product_id = sku.get(keys.PRODUCT_ID)
        for doc_id in sku.get("doc_ids"):
            doc = id_doc_pairs.get(doc_id, {})
            doc[keys.SKU_ID] = sku_id
            doc[keys.PRODUCT_ID] = product_id
            doc = {k: v for k, v in doc.items() if k in colnames}
            rows.append(doc)

    items = list(rows)
    df = pd.DataFrame(items).fillna("")
    cols = [
        c
        for c in colnames
        if c in df.columns
    ]
    df = df[cols]
    df = df.sort_values(keys.SKU_ID)
    df.to_excel(path, index=False)
    print("done")


if __name__ == "__main__":
    pass
