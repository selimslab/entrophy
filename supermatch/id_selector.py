import uuid


def select_unique_id(id_counts, used_ids, doc_ids):
    if id_counts:
        id_counts = dict(id_counts)
        most_common_id = max(id_counts, key=id_counts.get)
        if most_common_id not in used_ids:
            return most_common_id
    elif doc_ids:
        candidate_id = sorted(doc_ids)[0]
        if candidate_id not in used_ids:
            return candidate_id

    return str(uuid.uuid4())
