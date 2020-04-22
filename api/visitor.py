import itertools

from spiders.get_spiders import get_collectors
from spiders.visitor import run_spiders_concurrently
import sentry_sdk

sentry_sdk.init("https://39fd5a66307d47dcb3e9c37a8b709c44@sentry.io/5186400")



def visit_all():
    all_spiders = get_collectors()
    print(len(all_spiders), "spiders", all_spiders.keys())
    run_spiders_concurrently(all_spiders)


def debug_visit_all():
    all_spiders = get_collectors()
    print(len(all_spiders), "spiders", all_spiders.keys())
    run_spiders_concurrently(dict(itertools.islice(all_spiders.items(), 2)))


if __name__ == "__main__":
    visit_all()
