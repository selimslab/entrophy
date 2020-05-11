from dataclasses import dataclass, asdict

# spider keys
NAME = "name"
BARCODES = "barcodes"
MARKET = "market"
PRICE = "price"
LINK = "link"
SRC = "src"
BRAND = "brand"
CATEGORIES = "categories"
SUB_CATEGORIES = "sub_categories"

OUT_OF_STOCK = "out_of_stock"

HISTORICAL_PRICES = "historical_prices"

# google keys
GOOGLE_INFO = "google_info"
PROMOTED = "promoted"
VARIANTS = "variants"

# size
DIGITS = "digits"
UNIT = "unit"
SIZE = "size"

# gratis
VARIANT_NAME = "variant_name"

ALLOWED_KEYS = {
    BARCODES,
    NAME,
    MARKET,
    PRICE,
    LINK,
    SRC,
    BRAND,
    OUT_OF_STOCK,
    GOOGLE_INFO,
    PROMOTED,
    VARIANTS,
    DIGITS,
    UNIT,
    SIZE,
    VARIANT_NAME,
    CATEGORIES,
    SUB_CATEGORIES,
}

# helpers
PAGE_NUMBER = "page_number"
