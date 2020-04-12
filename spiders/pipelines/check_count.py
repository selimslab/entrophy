import constants as keys
import data_services


class ItemCountException(Exception):
    pass


def check_count(spider_name, stats):
    if spider_name == "marketyo":
        market = {"$in": keys.MARKETYO_MARKET_NAMES}
    else:
        market = spider_name
    count_items_in_stock = data_services.get_in_stock(market=market)
    item_count = stats.get("item_scraped_count", 0)
    is_visible_name = spider_name in keys.VISIBLE_MARKETS
    is_less_item = item_count < (count_items_in_stock / 4)
    is_problem = is_visible_name and is_less_item
    if is_problem:
        message = f"""
            {spider_name} seen {item_count} out of {count_items_in_stock}
            stats: {str(stats)}        
        """
        raise ItemCountException(message)
