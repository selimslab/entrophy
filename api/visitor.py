import itertools

from spiders.get_spiders import get_collectors
from spiders.visitor import run_spiders_simultaneously


def visit_all():
    all_spiders = get_collectors()
    print(len(all_spiders), "spiders", all_spiders.keys())
    # run_spiders_simultaneously(all_spiders)


def debug_visit_all():
    all_spiders = get_collectors()
    print(len(all_spiders), "spiders", all_spiders.keys())
    run_spiders_simultaneously(dict(itertools.islice(all_spiders.items(), 2)))


if __name__ == "__main__":
    visit_all()
