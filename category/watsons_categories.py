import requests
import bs4
from pprint import pprint
import services


def get_category_urls(base_url):
    r = requests.get(base_url)
    soup = bs4.BeautifulSoup(r.content, features="lxml")
    urls = list()
    links = soup.findAll("a", {"class": "main-menu-link"})
    for link in links:
        href = link.get("href")
        category = link.get("title")
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

for cat, url in urls:
    r = requests.get(url)
    soup = bs4.BeautifulSoup(r.content, "html.parser")
    cats = soup.find("div", {"class": "filter-item cats"})
    filters = [li.getText().strip() for li in cats.find("ul").findAll("a")]
    category_tree[cat]["cats"] = filters

    brands = soup.find("div", {"class": "filter-item marka"})
    filters = [li.getText().strip() for li in brands.find("ul").findAll("a")]
    category_tree[cat]["marka"] = filters

pprint(dict(category_tree))
services.save_json("filters/watsons_categories.json", dict(category_tree))
