import uuid


def select_unique_id(id_counts, doc_ids):
    if id_counts:
        id_counts = dict(id_counts)
        return max(id_counts, key=id_counts.get)
    if doc_ids:
        candidate_ids = [id for id in doc_ids if "clone" not in id]
        if candidate_ids:
            return sorted(candidate_ids)[0]

    return str(uuid.uuid4())
