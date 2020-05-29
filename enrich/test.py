from collections import defaultdict
from pprint import pprint

import services
from paths import input_dir, output_dir


def create_trees():
    ty_raw = services.read_json(input_dir / "ty_raw.json")

    watsons_raw = services.read_json(input_dir / "watsons_raw.json")

    pairs = services.read_json(input_dir / "brand_cat_pairs.json")

    cat_tree = defaultdict(set)
    brand_tree = defaultdict(set)

    original_brands = {}
    original_cats = {}

    def update(brands, subcats):

        clean_to_orig = {services.clean_name(b): b.lower() for b in brands}
        original_brands.update(clean_to_orig)
        brands = set(clean_to_orig.keys())

        clean_to_orig = {services.clean_name(c): c.lower() for c in subcats}
        original_cats.update(clean_to_orig)
        subcats = set(clean_to_orig.keys())

        for b in brands:
            brand_tree[b].update(subcats)

        for c in subcats:
            cat_tree[c].update(brands)

    for main_cat, filters in ty_raw.items():
        brands = filters.get("brand")
        subcats = filters.get("category")

        update(brands, subcats)

    for main_cat, filters in watsons_raw.items():
        brands = set(filters.get("marka"))
        subcats = set(filters.get("cats"))

        update(brands, subcats)

    for cat in pairs:
        brands = set(cat.get("brand"))
        subcats = set(cat.get("categories"))

        update(brands, subcats)

    brand_tree = {
        brand: [c for c in cats if c]
        for brand, cats in brand_tree.items()
        if len(brand) > 1
    }
    cat_tree = {
        cat: [c for c in brands if c]
        for cat, brands in cat_tree.items()
        if len(cat) > 1
    }

    services.save_json(input_dir / "brand_tree.json", brand_tree)

    services.save_json(input_dir / "cat_tree.json", cat_tree)

    services.save_json(input_dir / "original_brands.json", original_brands)

    services.save_json(input_dir / "original_cats.json", original_cats)


def inspect():
    brand_tree = services.read_json(input_dir / "brand_tree.json")
    # pprint(brand_tree.keys())

    brands_clean = services.read_json(output_dir / "brands_clean.json")

    brands_clean = [b for b in brands_clean if b]

    print(len(set(brands_clean).union(set(brand_tree.keys()))))

    diff = set(brands_clean).difference(set(brand_tree.keys()))
    pprint(diff)


def brand_variants():
    """
        johnson s baby -> johnsons baby

    """
    brand_tree = services.read_json(input_dir / "brand_tree.json")
    brands = brand_tree.keys()
    suspects = []  # with single tokens

    pprint(list(sorted(brands)))


if __name__ == "__main__":
    create_trees()
