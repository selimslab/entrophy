from tqdm import tqdm
from pprint import pprint
import logging
from collections import defaultdict
import services
from paths import output_dir, input_dir

from services import excel
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


def add_sku_id_and_product_id_to_pairs():
    # raw docs
    pairs = services.read_json(input_dir / "pairs.json")
    pairs = filter_pairs(pairs)

    skus = services.read_json(input_dir / "skus.json")
    pid_tree = get_pid_tree(skus)

    products_with_brand_and_sub_cat = services.read_json(
        output_dir / "products_with_brand_and_sub_cat.json"
    )

    def add_brand_and_subcat_to_doc(sku_id):
        sku = skus.get(sku_id, {})
        product_id = sku.get(keys.PRODUCT_ID)
        doc_ids = sku.get(keys.DOC_IDS, [])
        doc_ids = [id for id in doc_ids if "clone" not in id]
        if not doc_ids:
            return
        for doc_id in doc_ids:
            doc = pairs.get(doc_id)
            if not doc:
                continue
            doc["our_brand"] = product_with_brand_and_sub.get(keys.BRAND)
            doc[keys.SUBCAT] = product_with_brand_and_sub.get(keys.SUBCAT)
            doc[keys.PRODUCT_ID] = product_id
            doc[keys.SKU_ID] = sku_id

            pairs[doc_id] = doc

    logging.info("add_brand_and_subcat_to_doc..")
    for product_with_brand_and_sub in tqdm(products_with_brand_and_sub_cat):
        sku_id = product_with_brand_and_sub.get(keys.SKU_ID)

        if sku_id:
            add_brand_and_subcat_to_doc(sku_id)
        else:
            product_id = product_with_brand_and_sub.get(keys.PRODUCT_ID)
            sku_ids = pid_tree.get(product_id, [])
            for sku_id in sku_ids:
                add_brand_and_subcat_to_doc(sku_id)

    return pairs


def to_excel():
    pairs = add_sku_id_and_product_id_to_pairs()
    services.save_json(output_dir / "pairs_matched.json", pairs)
    rows = list(pairs.values())
    rows = [row for row in rows if keys.SKU_ID in row]
    excel.create_excel(rows, "../derived/jun10.xlsx")


if __name__ == "__main__":
    to_excel()
    # pairs = add_sku_id_and_product_id_to_pairs()
