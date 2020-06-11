import pathlib

cwd = pathlib.Path.cwd()
input_dir = cwd / "source"
output_dir = cwd / "derived"

skus_path = input_dir / "skus.json"
brand_subcats_pairs_path = output_dir / "brand_subcats_pairs.json"
