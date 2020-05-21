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


def create_category_tree():
    category_tree = services.tree()
    urls = get_category_urls("https://www.watsons.com.tr")
    for cat, url in urls:
        r = requests.get(url)
        soup = bs4.BeautifulSoup(r.content, "html.parser")
        cats = soup.find("div", {"class": "filter-item cats"})
        filters = [li.getText().strip() for li in cats.find("ul").findAll("a")]
        category_tree[cat]["cats"] = filters

        brands = soup.find("div", {"class": "filter-item marka"})
        filters = [li.getText().strip() for li in brands.find("ul").findAll("a")]
        category_tree[cat]["marka"] = filters

    pprint(category_tree)
    services.save_json("filters/watsons_categories.json", dict(category_tree))
