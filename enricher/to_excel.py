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


def add_brand_and_subcat_to_doc(sku, sku_id, product, pairs):
    brand = product.get(keys.BRAND)
    sub_brand = product.get(keys.SUB_BRAND)

    subcat = product.get(keys.SUBCAT)
    subcat_source = product.get(keys.SUBCAT_SOURCE)

    product_id = sku.get(keys.PRODUCT_ID)
    doc_ids = sku.get(keys.DOC_IDS, [])
    doc_ids = [id for id in doc_ids if "clone" not in id]
    if not doc_ids:
        return

    size = sku.get(keys.SIZE)
    color = sku.get(keys.SELECTED_COLOR)


    for doc_id in doc_ids:
        doc = pairs.get(doc_id)
        if not doc:
            continue
        doc["brand_assigned"] = brand
        doc[keys.SUB_BRAND] = sub_brand
        doc[keys.SUBCAT] = subcat
        doc["size_assigned"] = size
        doc["color_assigned"] = color
        doc[keys.SUBCAT_SOURCE] = subcat_source
        doc[keys.PRODUCT_ID] = product_id
        doc[keys.SKU_ID] = sku_id
        pairs[doc_id] = doc


def add_sku_id_and_product_id_to_pairs(products):
    # raw docs
    pairs = services.read_json(paths.pairs)
    pairs = filter_pairs(pairs)

    skus = services.read_json(paths.skus)
    pid_tree = get_pid_tree(skus)

    logging.info("add_brand_and_subcat_to_doc..")
    for product in tqdm(products):
        sku_id = product.get(keys.SKU_ID)

        if sku_id:
            sku = skus.get(sku_id, {})
            add_brand_and_subcat_to_doc(sku, sku_id, product, pairs)
        else:
            product_id = product.get(keys.PRODUCT_ID)
            sku_ids = pid_tree.get(product_id, [])
            for sku_id in sku_ids:
                sku = skus.get(sku_id, {})
                add_brand_and_subcat_to_doc(sku, sku_id, product, pairs)

    return pairs


def create_excel(products):
    colnames = [
        "product_id",
        "sku_id",
        "link",
        "name",
        # "clean_name",
        "digits",
        "unit",
        keys.VARIANT_NAME,
        keys.COLOR,
        "color_assigned",
        "size_assigned",
        # "size",
        "market",
        # "price",
        "barcodes",
        # keys.OUT_OF_STOCK,
        "brand",
        "brand_assigned",
        keys.SUB_BRAND,
        keys.CATEGORIES,
        keys.SUBCAT,
        keys.SUBCAT_SOURCE,
    ]

    pairs = add_sku_id_and_product_id_to_pairs(products)

    rows = list(pairs.values())
    rows = [row for row in rows if keys.SKU_ID in row]
    excel.create_excel(rows, "out/jun26.xlsx", colnames)


if __name__ == "__main__":
    products = services.read_json(paths.products_out)
    create_excel(products)
    # pairs = add_sku_id_and_product_id_to_pairs()
