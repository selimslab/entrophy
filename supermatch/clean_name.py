from tqdm import tqdm
import logging

import constants as keys
import services
from services.size_finder import size_finder, SizingException
import multiprocessing

def tokenize(s):
    stopwords = {"ml", "gr", "adet", "ve", "and", "ile"}
    try:
        tokens = set(t for t in s.split() if t not in stopwords)
        tokens = set(t for t in tokens if len(t) > 1 or t.isdigit())
        return tokens
    except AttributeError as e:
        logging.error(e)
        return set()


def replace_size(id, name):
    name = services.clean_name(name)
    if not name:
        return

    digits = unit = size_match = None
    try:
        digits, unit, size_match = size_finder.get_digits_unit_size(name)
        name = name.replace(size_match, str(digits) + " " + unit)
    except SizingException:
        pass
    finally:
        # only size can have .
        tokens = []
        for t in name.split():
            if len(t) <= 1:
                continue
            if not t.replace(".", "").isdigit():
                tokens.append(t.replace(".", " "))
            else:
                tokens.append(t)

        name = " ".join(tokens)
        return id, name, digits, unit, size_match


def add_clean_name(id_doc_pairs):
    logging.info("add_clean_name..")

    to_clean = list()
    for doc_id, doc in id_doc_pairs.items():
        if "name" in doc and "clean_name" not in doc:
            to_clean.append((doc_id, doc.get("name")))

    with multiprocessing.Pool(processes=2) as pool:
        results = pool.starmap(replace_size, tqdm(to_clean))
        results = (r for r in results if r)
        for doc_id, clean_name, digits, unit, size_match in results:
            info = {
                "clean_name": clean_name,
                keys.DIGITS: digits,
                keys.UNIT: unit,
                keys.SIZE: size_match,
            }
            id_doc_pairs[doc_id].update(info)
