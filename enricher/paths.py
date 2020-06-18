import pathlib

cwd = pathlib.Path.cwd()
input_dir = cwd / "in"
output_dir = cwd / "out"

pairs = cwd.parent / "test" / "in" / "pairs.json"

skus = cwd.parent / "test" / "out" / "skus.json"

brand_subcats_pairs = output_dir / "brand_subcats_pairs.json"
brand_pool = output_dir / "brand_pool.json"

color_original_to_clean = output_dir / "color_original_to_clean.json"

brand_original_to_clean = output_dir / "brand_original_to_clean.json"

subcat_original_to_clean = output_dir / "subcat_original_to_clean.json"

filtered_names_tree = output_dir / "filtered_names_tree.json"

products_filtered = output_dir / "products_filtered.json"

products_out = output_dir / "products_out.json"
