import services
from services.sizing.main import size_finder, SizingException
import itertools
import collections
from pprint import pprint
from dataclasses import dataclass, asdict
import services
from tqdm import tqdm
import multiprocessing
import operator


@dataclass
class Group:
    id: int
    names: list
    all_tokens: set = None
    common_tokens: set = None


def minitest():
    groups = {
        1: [
            "Vernel Max Taze Gül Çamaşır Yumuşatıcısı 1.44 L",
            "Vernel Konsantre Çamaşır Yumuşatıcısı Gül 1440 ml",
        ],
    }

    singles = {
        2: ["Vernel Gül Çamaşır Yumuşatıcısı 1.44L"],
        3: ["Vernel Konsantre Çamaşır Yumuşatıcısı Taze Gül 1440ml"],
        4: ["Vernel Konsantre Çamaşır Yumuşatıcısı Gül Ferahlığı 1440ml"],
    }

    inverted_index = collections.defaultdict(set)
    token_index = collections.defaultdict(set)
    common_index = collections.defaultdict(set)

    for id, names in itertools.chain(groups.items(), singles.items()):
        print(id)

        group_tokens = list()
        for name in names:
            name = services.clean_name(name)
            digits, unit, match = size_finder.get_digits_unit_size(
                services.clean_for_sizing(name)
            )
            name = name.replace(match, str(digits) + " " + unit)
            print(name)
            name_tokens = set(name.split())
            group_tokens.append(name_tokens)

        common_tokens = set.intersection(*group_tokens)
        all_tokens = set.union(*group_tokens)
        token_index[id] = all_tokens
        common_index[id] = common_tokens

    pprint(token_index)
    pprint(common_index)

    for id in singles.keys():
        common = common_index.get(id)
        for gid in groups:
            group_common = common_index.get(gid)
            if common.issuperset(group_common):
                group_all = token_index.get(gid)
                if group_all.issuperset(common):
                    print("match", id, gid)


def replace_size(id, name):
    name = services.clean_name(name)
    if not name:
        return
    try:
        digits, unit, match = size_finder.get_digits_unit_size(
            services.clean_for_sizing(name)
        )
        name = name.replace(match, str(digits) + " " + unit)
    except SizingException:
        pass
    finally:
        return id, name


def save_clean_names():
    with multiprocessing.Pool(processes=2) as pool:
        pairs = services.read_json("id_doc_pairs.json")
        names = ((id, doc.get("name")) for id, doc in tqdm(pairs.items()))
        names = ((id, name) for id, name in names if name)
        names = pool.starmap(replace_size, tqdm(list(names)))
        # services.save_json("names.json", names)


def add_clean_names():
    pairs = services.read_json("id_doc_pairs.json")
    names = services.read_json("names.json")
    for id, name in names:
        pairs[id]["clean_name"] = name
    services.save_json("pairs.json", pairs)


"""
save_clean_names()

"""
