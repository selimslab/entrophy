import pathlib

cwd = pathlib.Path.cwd()
temp = cwd / "temp"
indexes = cwd / "indexes"
cleaner = cwd / "cleaner"

guess_docs_path = temp / "guess_docs.json"

docs_with_brand_and_cat_path = temp / "docs_with_brand_and_cat.json"

cat_index_path = cwd / indexes / "cat_index.json"
brand_index_path = cwd / indexes / "brand_index.json"

clean_brands_path = cwd / cleaner / "clean_brands.json"
clean_cats_path = cwd / cleaner / "clean_cats.json"

catbr_summary_path = temp / "catbr_summary.json"
