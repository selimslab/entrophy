from tqdm import tqdm
import logging

import constants as keys
import services
from services.sizing.size_pattern_matcher import size_finder
import multiprocessing


def name_to_clean(doc_id, name):
    """
    clean
    remove all sizes
    remove barcodes
    """
    if not name:
        return
    clean_name = services.clean_string(name)

    # remove all sizes
    size_unit_tuples = size_finder.get_size_unit_tuples(clean_name)
    size_patterns_to_remove = [pattern for pattern, unit in size_unit_tuples]
    clean_name = services.remove_patterns_from_string(
        clean_name, size_patterns_to_remove
    )

    # filter tokens
    tokens = clean_name.split()
    tokens = services.remove_stopwords(tokens)
    barcode_tokens = [t for t in tokens if services.is_barcode(t)]
    tokens = [
        t
        for t in tokens
        if not services.is_single_letter(t) and t not in set(barcode_tokens)
    ]
    clean_name = " ".join(tokens)

    clean_name = services.remove_non_alpha_numeric_chars(clean_name)
    clean_name = services.remove_whitespace(clean_name)

    digit_unit_tuples = [
        services.size_pattern_to_digit_and_standard_unit(pattern, unit)
        for pattern, unit in size_unit_tuples
    ]

    digit_unit_tuples = [d for d in digit_unit_tuples if d]
    return doc_id, clean_name, digit_unit_tuples, barcode_tokens


def test_name_to_clean():
    cases = [
        "asfs 750ml 2 adet",
        "SUTAS YOGURT 1000 GR KAYMAKSIZ",
    ]
    for case in cases:
        print(name_to_clean(0, case))


def add_clean_name(id_doc_pairs):
    logging.info("add_clean_name..")

    to_clean = [(doc_id, doc.get(keys.NAME)) for doc_id, doc in id_doc_pairs.items()]

    # server memory not enough for more than 6 processes
    cpu_count = min(6, multiprocessing.cpu_count())
    logging.info(f"cpu_count {cpu_count}")

    with multiprocessing.Pool(processes=cpu_count) as pool:
        results = pool.starmap(name_to_clean, tqdm(to_clean))

    results = (r for r in results if r)
    for doc_id, clean_name, digit_unit_tuples, barcode_tokens in results:
        info = {
            keys.CLEAN_NAME: clean_name,
            keys.DIGIT_UNIT_TUPLES: digit_unit_tuples,
        }
        doc = id_doc_pairs[doc_id]
        doc.update(info)
        if barcode_tokens:
            doc[keys.BARCODES] = doc.get(keys.BARCODES, []) + barcode_tokens
        id_doc_pairs[doc_id] = doc
    return id_doc_pairs
