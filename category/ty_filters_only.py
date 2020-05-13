import requests
import bs4
from pprint import pprint
import services
import json


def get_links_to_crawl():
    url = "https://www.trendyol.com"
    r = requests.get(url)
    soup = bs4.BeautifulSoup(r.content, "html.parser")
    nav = soup.find("ul", {"class": "main-nav"})

    cats = []
    for menu in nav.findAll("li", class_="tab-link"):
        menu_title = menu.find("a", class_="category-header").text
        if "SÜPERMARKET" in menu_title or "KOZMETİK" in menu_title:
            navs = menu.findAll("ul", {"class": "sub-item-list"})
            for nav in navs:
                links = nav.findAll("a")
                hrefs = [link.get("href").split("/")[1] for link in links]
                cats += hrefs
    pprint(cats)
    return cats


all_cats = []


def get_sub_cats(category_name):
    url = f"https://api.trendyol.com/websearchgw/api/aggregations/{category_name}?culture=tr-TR&storefrontId=1&categoryRelevancyEnabled=undefined&priceAggregationType=DYNAMIC_GAUSS"
    r = requests.get(url)
    body = json.loads(r.content, strict=False)
    aggregations = body.get("result").get("aggregations")
    all_sub_cats = []
    for agg in aggregations:
        name = agg.get("group")
        filters = [val.get("beautifiedName") for val in agg.get("values")]
        all_sub_cats.append((name, filters))
        print(name)
        pprint(filters)
    all_cats.append((category_name, all_sub_cats))


def get_cats():
    for url in get_links_to_crawl():
        get_sub_cats(url)

    services.save_json("ty_filters.json", all_cats)


if __name__ == "__main__":
    pass
