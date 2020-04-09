import re

import constants as keys
import services


class ExactNameMatcher:
    @staticmethod
    def get_exact_match_groups(id_doc_pairs: dict, matched: set) -> list:
        print("creating exact_name_match_groups")
        pattern = re.compile("([^\s\w]|_)+")

        name_id_pairs = dict()
        name_barcode_pairs = dict()

        for doc_id, doc in id_doc_pairs.items():
            if doc_id in matched:
                continue
            name = doc.get(keys.NAME)
            if not name:
                continue
            try:
                name = pattern.sub("", name)
            except TypeError as e:
                print(e)

            name = services.clean_name(name).lower().strip()
            name = " ".join(sorted(name.split()))

            name_id_pairs[name] = name_id_pairs.get(name, []) + [doc_id]

            barcodes = doc.get(keys.BARCODES, [])
            name_barcode_pairs[name] = name_barcode_pairs.get(name, []) + barcodes

        exact_matches = list()
        for name, barcodes in name_barcode_pairs.items():
            barcodes = services.flatten(barcodes)
            barcodes = set(barcodes)
            if len(barcodes) <= 1:
                doc_ids = name_id_pairs.get(name)
                exact_matches.append(doc_ids)

        return exact_matches
