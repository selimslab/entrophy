import random


def select_unique_id(id_counts, used_ids, group):
    if id_counts:
        id_counts = dict(id_counts)
        unique_id = max(id_counts, key=id_counts.get)
    else:
        candidate_ids = [
            id
            for id in group
            if id not in used_ids and "clone" not in id
        ]
        if candidate_ids:
            unique_id = sorted(candidate_ids)[0]
        else:
            unique_id = sorted(group)[0] + str(random.randint(1, 100))
            while unique_id in used_ids:
                unique_id = sorted(group)[0] + str(random.randint(1, 100))

    return unique_id
