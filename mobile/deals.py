import pprint

import constants as keys
from mobile.deal_kw import antikws
from services import json_util
import data_services


def find_good_deals(skus):
    deals = list()
    deal_markets = {
        keys.MIGROS,
        keys.CARREFOUR,
        keys.CEPTESOK,
        keys.GRATIS,
        keys.WATSONS,
        keys.A101,
    }
    for sku in skus:
        name = sku.get(keys.NAME)
        if name:
            name = name.lower()
        if any([antikw in name for antikw in antikws]):
            continue

        price_pairs = {
            market: price
            for market, price in sku.get(keys.PRICES).items()
            if isinstance(price, (int, float))
        }

        if not price_pairs:
            continue

        best_market = min(price_pairs, key=price_pairs.get)
        if best_market not in deal_markets:
            continue

        prices = price_pairs.values()
        if len(prices) < 4:
            continue

        prices = sorted(list(prices))
        # compare the cheapest with 3th cheapest
        min_price = prices[0]
        max_price = prices[2]
        if float(min_price) < float(max_price) * 0.7:
            deal = {
                "name": sku.get("name"),
                "prices": price_pairs,
                "best_market": best_market,
                "best_price": price_pairs[best_market],
            }
            deals.append(deal)
            pprint.pprint(deal)

    return deals


def create_deals():
    deals = find_good_deals(data_services.elastic.scroll())
    json_util.save_json("deals.json", deals)


if __name__ == "__main__":
    create_deals()
