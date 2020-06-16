import pathlib

cwd = pathlib.Path.cwd()
input_dir = cwd / "in"
output_dir = cwd / "out"

skus = cwd.parent / "test" / "out" / "skus.json"

brand_subcats_pairs = output_dir / "brand_subcats_pairs.json"
brand_pool = output_dir / "brand_pool.json"
products_with_brand_and_subcat = output_dir / "products_with_brand_and_subcat_path.json"

colors = input_dir / "colors.json"

clean_colors = input_dir / "clean_colors.json"
