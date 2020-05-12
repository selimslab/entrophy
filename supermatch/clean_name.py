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
        size = size_finder.get_digits_unit_size(name)
        if size:
            digits, unit, size_match = size
            best_size = " ".join([str(digits), unit])
            name = name.replace(size_match, best_size)
    except SizingException:
        pass

    return id, name, digits, unit, size_match


def add_clean_name(id_doc_pairs, debug):
    logging.info("add_clean_name..")

    to_clean = list()
    for doc_id, doc in id_doc_pairs.items():
        if "name" in doc and "clean_name" not in doc:
            to_clean.append((doc_id, doc.get("name")))

    cpu_count = multiprocessing.cpu_count()
    logging.info(f"cpu_count {cpu_count}")

    if debug:
        with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
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
    else:
        # memory not enough for multiple procs on the server
        for doc_id, name in to_clean:
            result = replace_size(doc_id, name)
            if result:
                doc_id, clean_name, digits, unit, size_match = result
                info = {
                    "clean_name": clean_name,
                    keys.DIGITS: digits,
                    keys.UNIT: unit,
                    keys.SIZE: size_match,
                }
                id_doc_pairs[doc_id].update(info)
