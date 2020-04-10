from typing import Tuple

import constants as keys


def compare_docs(new_docs: dict, old_docs: dict) -> Tuple[list, list, list]:
    to_be_added = list()
    to_be_updated = list()
    ids_to_keep = set(new_docs.keys())

    for doc_id,new_doc in new_docs.items():
        old_doc = old_docs.get(doc_id, {})

        if not old_doc:
            to_be_added.append(new_doc)
            continue

        if new_doc != old_doc:
            to_be_updated.append(new_doc)

    existing_object_ids = set(object_id_doc_pairs.keys())
    ids_to_delete = list(existing_object_ids - ids_to_keep)

    print("to_be_added", len(to_be_added))
    print("to_be_updated", len(to_be_updated))
    print("to_be_deleted", len(ids_to_delete))

    return to_be_added, to_be_updated, ids_to_delete
