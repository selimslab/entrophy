from spiders.get_spiders import get_searchers
from spiders.visitor import run_spiders_simultaneously


def search_all():
    searchers = get_searchers()
    print(len(searchers), "searchers", searchers.keys())
    run_spiders_simultaneously(searchers)


if __name__ == "__main__":
    search_all()
