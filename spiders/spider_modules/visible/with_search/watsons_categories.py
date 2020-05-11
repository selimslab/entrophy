import requests
import bs4
from watsons_helper import WatsonsHelper
from pprint import pprint
import services

# urls = WatsonsHelper.get_category_urls("https://www.watsons.com.tr")

urls = ['https://www.watsons.com.tr/c/kisisel-bakim-302', 'https://www.watsons.com.tr/c/sac-307',
        'https://www.watsons.com.tr/c/cilt-322', 'https://www.watsons.com.tr/c/makyaj-281',
        'https://www.watsons.com.tr/c/anne-bebek-370', 'https://www.watsons.com.tr/c/erkek-298',
        'https://www.watsons.com.tr/c/k-beauty-545', 'https://www.watsons.com.tr/c/parfum-ve-deodorant-287',
        'https://www.watsons.com.tr/c/yasam-ve-spor-284', 'https://www.watsons.com.tr/c/elektronik-urunler-2882',
        'https://www.watsons.com.tr/c/supermarket-3753']

all_cats = []

for url in urls:
    r = requests.get(url)
    soup = bs4.BeautifulSoup(r.content, "html.parser")
    filters = soup.find("div", {"class": "filter-container"})
    uls = filters.findAll("ul")
    all_subcats = []
    for ul in uls:
        all_subcats += [li.getText().strip() for li in ul.findAll("a")]

    print(all_subcats)
    all_cats.append((url.split("/")[-1], all_subcats))

services.save_json("watsons_categories.json", all_cats)
