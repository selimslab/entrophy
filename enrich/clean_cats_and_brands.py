import services


def clean_cats_and_brands():
    cats = services.read_json("cleaner/joined_categories.json")
    cats = cats.get("categories")
    clean_cats = services.list_to_clean_set(cats)
    services.save_json("cleaner/clean_cats.json", clean_cats)

    brands = services.read_json("cleaner/joined_brands.json")
    brands = brands.get("brands")
    clean_brands = services.list_to_clean_set(brands)
    services.save_json("cleaner/clean_brands.json", clean_brands)
