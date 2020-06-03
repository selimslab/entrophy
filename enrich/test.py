from paths import input_dir, output_dir
import services

if __name__ == "__main__":
    brand_subcats_pairs_path = output_dir / "brand_subcats_pairs.json"
    brand_subcats_pairs = services.read_json(brand_subcats_pairs_path)
    print(sorted(list(brand_subcats_pairs.keys()), key=len, reverse=True))
