import os
import re

import services.collections_util
import services
import constants as keys

from paths import *

from data_services.mongo.collections import items_collection


def get_ty_colors():
    ty_colors = items_collection.distinct("color", {keys.MARKET: "ty"})
    services.save_json(temp / "ty_colors.json", ty_colors)


def get_all_colors():
    color_path = temp / "colors.json"
    if not os.path.exists(color_path):
        colors = items_collection.distinct("color")
        print(colors)
        services.save_json(color_path, colors)
    else:
        colors = services.read_json(color_path)
    return colors


def clean_colors(colors):
    clean_colors = list_to_clean_set(colors)
    clean_colors = [c for c in clean_colors
                    if not c.isdigit() and "nocolor" not in c]

    letters_only = re.compile(r"[^a-z]")

    clean_colors = [
        " ".join(
            re.sub(letters_only, "", t).strip()
            for t in color.split()
        ).strip()
        for color in clean_colors
    ]
    clean_colors = list(set(clean_colors))
    clean_color_path = temp / "clean_colors.json"
    services.save_json(clean_color_path, clean_colors)
