import pathlib

cwd = pathlib.Path.cwd()
input_dir = cwd / "in"
output_dir = cwd / "out"

skus = cwd.parent / "test" / "out" / "skus.json"

brand_subcats_pairs = output_dir / "brand_subcats_pairs.json"
brand_pool = output_dir / "brand_pool.json"

products_with_brand_and_subcat = output_dir / "products_with_brand_and_subcat.json"
products_filtered = output_dir / "products_filtered.json"

color_original_to_clean = output_dir / "color_original_to_clean.json"

brand_original_to_clean = output_dir / "brand_original_to_clean.json"

subcat_original_to_clean = output_dir / "subcat_original_to_clean.json"
