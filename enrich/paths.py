import pathlib

cwd = pathlib.Path.cwd()
temp = cwd / "temp"

full_skus_path = temp / "full_skus.json"

indexes = cwd / "indexes"
cleaner = cwd / "cleaner"

guess_docs_path = temp / "guess_docs.json"

docs_with_brand_and_cat_path = temp / "docs_with_brand_and_cat.json"

cat_index_path = indexes / "cat_index.json"
brand_index_path = indexes / "brand_index.json"

clean_brands_path = cleaner / "clean_brands.json"
clean_cats_path = cleaner / "clean_cats.json"

catbr_summary_path = temp / "catbr_summary.json"
