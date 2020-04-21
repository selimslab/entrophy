import services
import timeit
from services import name_cleaner
from services.sizing.main import size_finder, SizingException

import multiprocessing
from tqdm import tqdm


def get_size(name="apti"):
    try:
        size_name = name_cleaner.clean_for_sizing(name)
        result = size_finder.get_digits_unit_size(size_name)
        if result:
            return result
    except SizingException:
        pass


def par():
    with multiprocessing.Pool(processes=2) as pool:
        pool.map(get_size, tqdm(names))


def seq():
    for name in tqdm(names):
        get_size(name)


if __name__ == '__main__':
    names = services.read_json("names.json")
    print(timeit.timeit("par()", setup="from __main__ import par, get_size", number=1))
    print(timeit.timeit("seq()", setup="from __main__ import seq, get_size", number=1))
