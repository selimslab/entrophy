from collections import Counter, OrderedDict, defaultdict

from tqdm import tqdm

import services
from paths import output_dir, input_dir

from services import excel
import constants as keys


def to_excel():
    full_skus = services.read_json(input_dir / "full_skus.json")
    processed_docs = services.read_json(input_dir / "processed_docs.json")
    skus_with_brand_and_sub_cat = services.read_json(
        output_dir / "skus_with_brand_and_sub_cat.json"
    )
    for sku in tqdm(skus_with_brand_and_sub_cat):
        sku_id = sku.get("sku_id")
        doc_ids = full_skus.get(sku_id).get(keys.DOC_IDS, [])
        if doc_ids:
            for doc_id in doc_ids:
                processed_docs[doc_id]["our_brand"] = sku.get(keys.BRAND)
                processed_docs[doc_id][keys.SUBCAT] = sku.get(keys.SUBCAT)

    excel.create_excel(processed_docs.values(), "jun8.xlsx")


def create_product_groups():
    full_skus = services.read_json(input_dir / "full_skus.json")

    relevant_keys = {
        keys.CATEGORIES,
        keys.BRANDS_MULTIPLE,
        keys.CLEAN_NAMES,
        keys.SKU_ID,
        keys.PRODUCT_ID,
    }

    groups = defaultdict(list)
    singles = []
    for sku_id, sku in full_skus.items():
        sku = services.filter_keys(sku, relevant_keys)
        if keys.PRODUCT_ID in sku:
            pid = sku.get(keys.PRODUCT_ID)
            groups[pid].append(sku)
        else:
            singles.append(sku)

    for pid, docs in groups.items():
        brands = [doc.get(keys.BRANDS_MULTIPLE) for doc in docs]
        cats = [doc.get(keys.CATEGORIES) for doc in docs]
        clean_names = [doc.get(keys.CLEAN_NAMES) for doc in docs]

        product = {
            keys.PRODUCT_ID: pid,
            keys.BRANDS_MULTIPLE: services.flatten(brands),
            keys.CATEGORIES: services.flatten(cats),
            keys.CLEAN_NAMES: services.flatten(clean_names),
        }
        singles.append(product)

    services.save_json(input_dir / "products.json", singles)


if __name__ == "__main__":
    create_product_groups()
