import multiprocessing
from tqdm import tqdm
import logging

from typing import List

import services
import constants as keys

from subcat import clean_sub_cats


def clean_brands(brands: list) -> list:
    return services.clean_list_of_strings(services.flatten(brands))


def add_clean_brand(sku: dict) -> dict:
    sku[keys.CLEAN_BRANDS] = clean_brands(sku.get("brands", []))
    return sku


def clean_cats(cats: list) -> list:
    return services.clean_list_of_strings(services.flatten(cats))


def add_clean_cats(sku: dict) -> dict:
    cats = sku.get(keys.CATEGORIES, [])
    sku[keys.CLEAN_CATS] = clean_cats(cats)
    return sku


def add_clean_subcats(sku: dict) -> dict:
    cats = sku.get(keys.CATEGORIES, [])
    sku[keys.CLEAN_SUBCATS] = clean_sub_cats(cats)
    return sku


def get_clean_products(skus: List[dict]):
    relevant_keys = {
        keys.CATEGORIES,
        keys.BRANDS_MULTIPLE,
        keys.CLEAN_NAMES,
        keys.SKU_ID,
        keys.PRODUCT_ID,
    }
    skus = [services.filter_keys(doc, relevant_keys) for doc in skus]

    logging.info("cleaning brands, cats, and subcats..")
    with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
        skus = pool.map(add_clean_brand, tqdm(skus))
        skus = pool.map(add_clean_cats, tqdm(skus))
        skus = pool.map(add_clean_subcats, tqdm(skus))

    return skus
