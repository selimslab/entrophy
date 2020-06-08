import services
import constants as keys
from paths import output_dir


def test_sub_brand():
    """ test to find sub brands """

    brand_pool = services.read_json(output_dir / "brand_pool.json")
    name_brand_subcat = services.read_json(output_dir / "name_brand_subcat.json")

    path = output_dir / "most_frequent_start_strings.json"
    freq = services.read_json(path)

    for doc in name_brand_subcat:
        brand = doc.get(keys.BRAND, "")
        if not brand:
            continue

        brand_tokens = brand.split()
        if len(brand_tokens) == 1:
            continue
        brand_freq = {}
        for i in range(1, len(brand_tokens)):
            root = " ".join(brand_tokens[:i])
            if root in brand_pool:
                count = freq.get(root, 0)
                brand_freq[root] = count

        root_brand = services.get_most_frequent_key(brand_freq)
        if root_brand:
            print((brand, root_brand))
            doc[keys.BRAND] = root_brand
            doc[keys.SUB_BRAND] = brand

    print("with_subbrand", services.count_fields(name_brand_subcat, keys.SUB_BRAND))
    services.save_json(output_dir / "with_subbrand.json", name_brand_subcat)
