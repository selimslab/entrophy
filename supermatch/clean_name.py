from tqdm import tqdm
import logging

import constants as keys
import services
from services.size_pattern_matcher import size_finder
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


def name_to_clean(doc_id, name):
    if not name:
        return
    clean_name = services.clean_string(name)
    clean_name, raw_size_unit_tuples = size_finder.get_name_without_size_and_all_matched_size_patterns(clean_name)
    digit_unit_tuples = [size_finder.size_pattern_to_digit_unit(raw_size, unit)
                         for raw_size, unit in raw_size_unit_tuples]
    digit_unit_tuples = [d for d in digit_unit_tuples if d]
    return doc_id, clean_name, digit_unit_tuples


def add_clean_name(id_doc_pairs):
    logging.info("add_clean_name..")

    cpu_count = multiprocessing.cpu_count()
    logging.info(f"cpu_count {cpu_count}")
    cpu_count = min(6, cpu_count)  # server memory not enough for more than 6 processes

    to_clean = [(doc_id, doc.get(keys.NAME)) for doc_id, doc in id_doc_pairs.items()]
    with multiprocessing.Pool(processes=cpu_count) as pool:
        results = pool.starmap(name_to_clean, tqdm(to_clean))

    results = (r for r in results if r)
    for doc_id, clean_name, digit_unit_tuples in results:
        info = {
            keys.CLEAN_NAME: clean_name,
            keys.DIGIT_UNIT_TUPLES: digit_unit_tuples,
        }
        id_doc_pairs[doc_id].update(info)
