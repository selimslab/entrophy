import services

from paths import *
from .count_fields import stat


def summarize_cats():
    docs_with_brand_and_cat = services.read_json(docs_with_brand_and_cat_path)
    catbr_summary = [
        {
            k: v
            for k, v in doc.items()
            if k in {"clean_names", "brand", "cat", "top_brand_guess", "top_cat_guess"}
        }
        for doc in docs_with_brand_and_cat
    ]
    services.save_json(catbr_summary_path, catbr_summary)

    stat(docs_with_brand_and_cat)
