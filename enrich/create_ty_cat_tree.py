import requests
import bs4
from pprint import pprint
import services
import json

from paths import input_dir


def get_category_names():
    url = "https://www.trendyol.com"
    r = requests.get(url)
    soup = bs4.BeautifulSoup(r.content, "html.parser")
    nav = soup.find("ul", {"class": "main-nav"})

    category_names = []
    for menu in nav.findAll("li", class_="tab-link"):
        menu_title = menu.find("a", class_="category-header").text
        if "SÜPERMARKET" in menu_title or "KOZMETİK" in menu_title:
            navs = menu.findAll("ul", {"class": "sub-item-list"})
            for nav in navs:
                links = nav.findAll("a")
                hrefs = [link.get("href").split("/")[1] for link in links]
                category_names += hrefs
    return category_names


def update_category_tree(category_name, category_tree):
    url = f"https://api.trendyol.com/websearchgw/api/aggregations/{category_name}?culture=tr-TR&storefrontId=1&categoryRelevancyEnabled=undefined&priceAggregationType=DYNAMIC_GAUSS"
    r = requests.get(url)
    body = json.loads(r.content, strict=False)
    aggregations = body.get("result").get("aggregations")
    for agg in aggregations:
        filter_name = agg.get("group", "")
        category_tree[category_name][filter_name.lower()] = [
            val.get("beautifiedName", "").lower() for val in agg.get("values")
        ]


def get_cats():
    category_tree = services.tree()
    category_names = get_category_names()
    pprint(category_names)
    for category_name in category_names:
        update_category_tree(category_name, category_tree)
    services.save_json(input_dir / "ty_cat_tree", category_tree)


if __name__ == "__main__":
    get_cats()
