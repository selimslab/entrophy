from tqdm import tqdm
import logging
from collections import defaultdict
import services
import paths as paths

from services.files import excel
import constants as keys


def get_pid_tree(skus):
    logging.info("pid_tree..")
    pid_tree = defaultdict(set)
    for sku in skus.values():
        sku_id = sku.get(keys.SKU_ID)
        pid = sku.get(keys.PRODUCT_ID)
        if pid and sku_id:
            pid_tree[pid].add(sku_id)
    return pid_tree


def filter_pairs(pairs):
    # filter_pairs, erase old sku_ids and pids from pairs

    return {
        id: {k: v for k, v in doc.items() if k not in {keys.PRODUCT_ID, keys.SKU_ID}}
        for id, doc in pairs.items()
        if "clone" not in id
    }


def add_brand_and_subcat_to_doc(sku, sku_id, pairs, brand, subcat):
    product_id = sku.get(keys.PRODUCT_ID)
    doc_ids = sku.get(keys.DOC_IDS, [])
    doc_ids = [id for id in doc_ids if "clone" not in id]
    if not doc_ids:
        return

    for doc_id in doc_ids:
        doc = pairs.get(doc_id)
        if not doc:
            continue
        doc["our_brand"] = brand
        doc[keys.SUBCAT] = subcat
        doc[keys.PRODUCT_ID] = product_id
        doc[keys.SKU_ID] = sku_id
        # if keys.SUBCAT in doc and keys.SUBCAT_CANDIDATES not in doc:

        pairs[doc_id] = doc


def add_sku_id_and_product_id_to_pairs():
    # raw docs
    pairs = services.read_json(paths.pairs)
    pairs = filter_pairs(pairs)

    skus = services.read_json(paths.skus)
    pid_tree = get_pid_tree(skus)

    products = services.read_json(
        paths.products_out
    )

    def sync(sku_id):
        sku = skus.get(sku_id, {})
        brand = doc.get(keys.BRAND)
        subcat = doc.get(keys.SUBCAT)
        add_brand_and_subcat_to_doc(sku, sku_id, pairs, brand, subcat)

    logging.info("add_brand_and_subcat_to_doc..")
    for doc in tqdm(products):
        sku_id = doc.get(keys.SKU_ID)

        if sku_id:
            sync(sku_id)
        else:
            product_id = doc.get(keys.PRODUCT_ID)
            sku_ids = pid_tree.get(product_id, [])
            for sku_id in sku_ids:
                sync(sku_id)

    return pairs


def to_excel():
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
    pairs = add_sku_id_and_product_id_to_pairs()
    # services.save_json(output_dir / "pairs_matched.json", pairs)
    rows = list(pairs.values())
    rows = [row for row in rows if keys.SKU_ID in row]
    excel.create_excel(rows, "out/jun19.xlsx", colnames)


if __name__ == "__main__":
    to_excel()
    # pairs = add_sku_id_and_product_id_to_pairs()