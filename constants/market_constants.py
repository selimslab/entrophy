from constants.helper_markets import *
from constants.marketyo import *
from constants.top8 import *
from constants.top_local import *

TRENDYOL = "ty"

TOP_LOCAL += MARKETYO_MARKET_NAMES

ALL_MARKETS = TOP8 + TOP_LOCAL + HELPER_MARKETS + [TRENDYOL]

MATCHING_MARKETS = [m for m in ALL_MARKETS if m not in {GROSERI}]

ALLOWED_MARKET_LINKS = TOP8 + ["rossmann", "eveshop"] + TOP_LOCAL + HELPER_MARKETS
ALLOWED_MARKET_LINKS = [
    name
    for name in ALLOWED_MARKET_LINKS
    if name not in {MARKET_PAKETI, ROSSMANN, EVESHOP}
]

VISIBLE_MARKETS = TOP8 + TOP_LOCAL + ["marketyo", TRENDYOL]
VISIBLE_MARKETS.remove(CEPTESOK)

COSMETICS_MARKETS = [GRATIS, WATSONS, EVESHOP, ROSSMANN, COSMETICA, SEVIL, PERFUMEPOINT]
BABY_MARKETS = [CIVIL, JOKER]
TRADITIONAL_MARKETS = list(
    set(ALL_MARKETS) - set(COSMETICS_MARKETS) - set(BABY_MARKETS)
)
