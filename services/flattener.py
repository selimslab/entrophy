def flatten(l: list) -> list:
    flat_list = []
    for i in l:
        if not isinstance(i, list):
            flat_list.append(i)
        else:
            flat_list += flatten(i)
    return flat_list
