from collections import Counter
import constants as keys


def get_brand_freq(products, brand_original_to_clean):
    """  how many items has been given this  brand by a vendor

    "erikli": 89,
    "damla": 13,
    "torku": 929

    """
    brand_freq = Counter()

    for product in products:
        brands = product.get(keys.BRANDS_MULTIPLE, [])
        clean_brands = [brand_original_to_clean.get(b) for b in brands]
        brand_freq.update(clean_brands)

    return brand_freq


def get_subcat_freq(products, subcat_original_to_clean):
    """  how many items has been given this subcat by a vendor """

    subcat_freq = Counter()

    for product in products:
        subcats = product.get(keys.SUB_CATEGORIES, [])
        clean_subcats = [subcat_original_to_clean.get(s) for s in subcats]
        subcat_freq.update(clean_subcats)

    return subcat_freq