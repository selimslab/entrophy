import requests
from bs4 import BeautifulSoup

import constants as keys


class HepsiburadaHelper:
    @staticmethod
    def extract_product_info(response) -> dict:
        pass

    @staticmethod
    def get_categories(html_path):
        soup = (open(html_path, mode="r", encoding="utf-8")).read()
        soup = BeautifulSoup(soup, "html.parser")
        categories = dict()
        categories["category"] = []
        hb_menu = soup.findAll("li", class_="MenuItems-1-U3X")
        print(hb_menu)
        # for submenu in soup:
        #     for category in submenu.findAll("li"):
        #         if not category.get('class'):
        #             categories['category'].append((category.find('a').text).replace('|', '').strip())
        # return categories


HepsiburadaHelper.get_categories("Hepsiburada.com.html")
