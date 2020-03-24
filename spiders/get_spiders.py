from scrapy import spiderloader
from scrapy.utils import project

import constants as keys


def get_searchers():
    settings = project.get_project_settings()
    spider_loader = spiderloader.SpiderLoader.from_settings(settings)
    spider_names = spider_loader.list()
    spider_names = [name for name in spider_names if "search" in name]
    spider_names = [
        s for s in spider_names if not any([b in s for b in keys.HELPER_MARKETS])
    ]
    all_spiders = {name: spider_loader.load(name) for name in spider_names}
    return all_spiders


def get_collectors():
    settings = project.get_project_settings()
    spider_loader = spiderloader.SpiderLoader.from_settings(settings)
    spider_names = spider_loader.list()
    spider_names = [name for name in spider_names if name in keys.VISIBLE_MARKETS]
    all_spiders = {name: spider_loader.load(name) for name in spider_names}
    return all_spiders


if __name__ == "__main__":
    print(get_collectors())
