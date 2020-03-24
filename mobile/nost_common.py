from collections import Counter

from tqdm import tqdm

import constants as keys
import data_services.mongo.collections as collections
from services import flattener
from services.name_cleaner import clean_name


def get_most_common_tokens():
    projection = {keys.NAME: 1}
    names = list()
    cursor = collections.items_collection.find({}, projection)
    for doc in tqdm(cursor):
        name = doc.get(keys.NAME)
        names.append(name)

    tokens = [clean_name(name).lower().split()[0] for name in names if name]
    tokens = flattener.flatten(tokens)

    most_common = Counter(tokens).most_common(2000)
    most_common = [token_count_pair[0] for token_count_pair in most_common]
    most_common = [token for token in most_common if len(token) > 2]
    return most_common
