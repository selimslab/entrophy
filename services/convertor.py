import logging


def convert_price(price: str):
    dot_split = str(price).split(".")
    if len(dot_split) == 3:
        price = ".".join(dot_split[:2])
    try:
        price = float(price)
    except (ValueError, TypeError) as e:
        logging.error(e)
        raise

    price = round(price, 2)
    if price.is_integer():
        price = int(price)

    return price
