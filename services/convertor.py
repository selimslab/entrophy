import logging
from typing import Union


def convert_price(price: str) -> Union[int, float, None]:
    price = (
        str(price)
            .lower()
            .replace("tl", "")
            .replace("₺", "")
            .replace("try", "")
            .replace(" ", "")
            .strip()
    )

    dot_split = str(price).split(".")
    if len(dot_split) == 3:
        price = ".".join(dot_split[:2])
    if not price:
        return

    try:
        price = float(price)
    except (ValueError, TypeError) as e:
        logging.error(e)
        return

    price = round(price, 2)
    if price.is_integer():
        price = int(price)

    return price
