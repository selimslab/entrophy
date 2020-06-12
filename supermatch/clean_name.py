from tqdm import tqdm
import logging

import constants as keys
import services
from services.size_pattern_matcher import size_finder
import multiprocessing


def name_to_clean(doc_id, name):
    """
    clean
    remove all sizes
    """
    if not name:
        return
    clean_name = services.clean_string(name)
    size_unit_tuples = size_finder.get_size_unit_tuples(clean_name)
    size_patterns_to_remove = [pattern for pattern, unit in size_unit_tuples]
    clean_name_no_size = services.remove_patterns_from_string(clean_name, size_patterns_to_remove)

    digit_unit_tuples = [
        size_finder.size_pattern_to_digit_unit(pattern, unit)
        for pattern, unit in size_unit_tuples
    ]

    digit_unit_tuples = [d for d in digit_unit_tuples if d]
    return doc_id, clean_name_no_size, digit_unit_tuples


def remove_stopwords(tokens: list) -> list:
    stopwords = {"ml", "gr", "kg", "adet", "ve", "and", "ile", "for", "icin"}
    return [t for t in tokens if t not in stopwords]


def filter_tokens(s):
    try:
        tokens = s.split()
        tokens = remove_stopwords(tokens)
        tokens = set(t for t in set(tokens) if len(t) > 1 or t.isdigit())  # single digits may stay but not letters
        return tokens
    except AttributeError as e:
        logging.error(e)
        return set()


def add_clean_name(id_doc_pairs):
    logging.info("add_clean_name..")

    to_clean = [(doc_id, doc.get(keys.NAME)) for doc_id, doc in id_doc_pairs.items()]

    # server memory not enough for more than 6 processes
    cpu_count = min(6, multiprocessing.cpu_count())
    logging.info(f"cpu_count {cpu_count}")

    with multiprocessing.Pool(processes=cpu_count) as pool:
        results = pool.starmap(name_to_clean, tqdm(to_clean))

    results = (r for r in results if r)
    for doc_id, clean_name, digit_unit_tuples in results:
        info = {
            keys.CLEAN_NAME: clean_name,
            keys.DIGIT_UNIT_TUPLES: digit_unit_tuples,
        }
        id_doc_pairs[doc_id].update(info)

    return id_doc_pairs
