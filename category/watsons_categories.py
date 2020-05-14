import requests
import bs4
from spiders.spider_modules.visible.with_search.watsons_helper import WatsonsHelper
from pprint import pprint
import services


# urls = WatsonsHelper.get_category_urls("https://www.watsons.com.tr")


def get_category_urls(base_url):
    r = requests.get(base_url)
    soup = bs4.BeautifulSoup(r.content, features="lxml")
    urls = list()
    links = soup.findAll("a", {"class": "main-menu-link"})
    for link in links:
        href = link.get("href")
        category = link.get_text().strip()
        url = base_url + href
        if "sayfa" not in url and url not in urls:
            urls.append((category, url))

    return urls


urls = get_category_urls("https://www.watsons.com.tr")

# Define recursive dictionary
from collections import defaultdict


def tree():
    return defaultdict(tree)


category_tree = tree()

for cat, url in urls[:1]:
    r = requests.get(url)
    soup = bs4.BeautifulSoup(r.content, "html.parser")
    containers = soup.findAll("div", {"class": "filter-item"})
    for con in containers:
        name = con.find("div", {"class": "spec-filter-head"}) or con.find("span", {"class": "spec-filter-head"})
        if name:
            name = name.get("data-attribute-name") or name.get_text()
            name = name.strip()
        ul = con.find("ul")
        filters = [li.getText().strip() for li in ul.findAll("a")]

        category_tree[cat][name] = filters

pprint(category_tree)
# services.save_json("watsons_categories.json", all_cats)
