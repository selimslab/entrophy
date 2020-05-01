from dataclasses import dataclass, asdict
# spider keys
NAME = "name"
BARCODES = "barcodes"
MARKET = "market"
PRICE = "price"
LINK = "link"
SRC = "src"
BRAND = "brand"
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
}

# helpers
PAGE_NUMBER = "page_number"

