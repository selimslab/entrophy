import copy
import string
from dataclasses import asdict

import constants as keys
import data_models
import services
from .id_creator import create_product_id
import logging


def reduce_skus_to_products(id_sku_pairs, groups_of_sku_ids, sku_id_gratis_name_pairs):

    used_product_ids = set()
    skus_covered_in_products_count = 0
    multi_sku_product_count = 0

    for sku_ids in groups_of_sku_ids:
        if len(sku_ids) == 1:
            sku_id = sku_ids.pop()
            used_product_ids.add(sku_id)
            continue

        skus = [id_sku_pairs.get(id) for id in sku_ids]
        links = [sku.get("links") for sku in skus]

        markets = [sku.get(keys.MARKETS) for sku in skus]
        markets = services.flatten(markets)
        markets = [m for m in markets if m]
        markets = list(set(markets))
        markets.sort()
        if not markets:
            print("no markets for", sku_ids)
            continue

        sku_ids_with_gratis_name = [
            sku_id for sku_id in sku_ids if sku_id in sku_id_gratis_name_pairs
        ]
        gratis_names = [
            sku_id_gratis_name_pairs.get(sku_id, "")
            for sku_id in sku_ids_with_gratis_name
        ]
        if gratis_names:
            product_name = gratis_names.pop()
        else:
            names = [sku.get(keys.NAME) for sku in skus]
            names = [n for n in names if n]
            if not names:
                logging.info(f"no product name for {sku_ids}")
                continue
            product_name = sorted(names, key=len)[0]
            size_name = services.size_cleaner(product_name)
            matched = services.size_finder.pattern_match(size_name)
            if matched:
                match, unit = matched
                product_name = size_name.replace(match, "").strip()
                product_name = string.capwords(product_name)

        sku_tags = [sku.get(keys.TAGS, []) for sku in skus]
        tokens = services.get_tokens_of_a_group(sku_tags)
        tags = list(set(tokens))
        # tags = " ".join(sorted(tokens))

        src = None
        srcs = [sku.get(keys.SRC) for sku in skus]
        srcs = [s for s in srcs if s]
        if srcs:
            src = sorted(srcs, key=len)[0]

        product_id = create_product_id(skus, sku_ids, used_product_ids)
        used_product_ids.add(product_id)

        barcodes = [sku.get(keys.BARCODES) for sku in skus]
        barcodes = services.flatten(barcodes)
        barcodes = [b for b in barcodes if b]

        product = data_models.Product(
            links=links,
            name=product_name,
            markets=markets,
            market_count=len(markets),
            tags=tags,
            variants=sku_ids,
            src=src,
            objectID=product_id,
            barcodes=barcodes,
        )
        for sku_id in sku_ids:
            del id_sku_pairs[sku_id]
        id_sku_pairs[product_id] = asdict(product)
        skus_covered_in_products_count += len(sku_ids)
        multi_sku_product_count += 1

    products = list(id_sku_pairs.values())
    products = [p for p in products if p]

    print(
        "covering",
        skus_covered_in_products_count,
        "skus in",
        multi_sku_product_count,
        "multi_sku_products",
    )

    return products
