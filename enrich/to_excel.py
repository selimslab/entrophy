from tqdm import tqdm
from pprint import pprint
import logging
from collections import defaultdict
import services
from paths import output_dir, input_dir

from services import excel
import constants as keys


def add_sku_id_and_product_id_to_pairs():
    skus = services.read_json(input_dir / "skus.json")
    pairs = services.read_json(input_dir / "pairs.json")

    products_with_brand_and_sub_cat = services.read_json(
        output_dir / "products_with_brand_and_sub_cat.json"
    )

    logging.info("pid_tree..")
    pid_tree = defaultdict(set)
    for sku in skus.values():
        sku_id = sku.get(keys.SKU_ID)
        pid = sku.get(keys.PRODUCT_ID)
        if pid and sku_id:
            pid_tree[pid].add(sku_id)

    def add_brand_and_subcat_to_doc(sku_id):
        sku = skus.get(sku_id, {})
        product_id = sku.get(keys.PRODUCT_ID)

        doc_ids = sku.get(keys.DOC_IDS, [])
        if doc_ids:
            for doc_id in doc_ids:
                doc = pairs[doc_id]
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
    excel.create_excel(pairs.values(), "jun9.xlsx")


if __name__ == "__main__":
    to_excel()
    # pairs = add_sku_id_and_product_id_to_pairs()

