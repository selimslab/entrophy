import uuid


def select_unique_id(id_counts, doc_ids, used_ids):
    if id_counts:
        id_counts = dict(id_counts)
        most_common_id = max(id_counts, key=id_counts.get)
        if most_common_id not in used_ids:
            return most_common_id
    if doc_ids:
        candidate_ids = [id for id in doc_ids if "clone" not in id]
        if candidate_ids:
            cid = sorted(candidate_ids)[0]
            if cid not in used_ids:
                return cid

    return str(uuid.uuid4())
