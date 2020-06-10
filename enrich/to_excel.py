from tqdm import tqdm

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
    for sku in tqdm(products_with_brand_and_sub_cat):
        sku_id = sku.get("sku_id")
        product_id = sku.get(keys.PRODUCT_ID)
        doc_ids = skus.get(sku_id, {}).get(keys.DOC_IDS, [])
        if doc_ids:
            for doc_id in doc_ids:
                pairs[doc_id]["our_brand"] = sku.get(keys.BRAND)
                pairs[doc_id][keys.SUBCAT] = sku.get(keys.SUBCAT)
                pairs[doc_id][keys.PRODUCT_ID] = product_id
                pairs[doc_id][keys.SKU_ID] = sku_id
    return pairs


def to_excel():
    pairs = add_sku_id_and_product_id_to_pairs()
    services.save_json(output_dir / "pairs_matched.json", pairs)
    excel.create_excel(pairs.values(), "jun9.xlsx")


if __name__ == "__main__":
    to_excel()
