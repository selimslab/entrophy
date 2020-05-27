import os
import re

import services
import constants as keys

from paths import input_dir, output_dir

from data_services.mongo.collections import items_collection


def get_ty_colors():
    ty_colors = items_collection.distinct("color", {keys.MARKET: "ty"})
    services.save_json(input_dir / "ty_colors.json", ty_colors)


def get_all_colors():
    color_path = input_dir / "colors.json"
    if not os.path.exists(color_path):
        colors = items_collection.distinct("color")
        print(colors)
        services.save_json(color_path, colors)
    else:
        colors = services.read_json(color_path)
    return colors


def clean_colors(colors):
    clean_colors = services.list_to_clean_set(colors)
    clean_colors = [c for c in clean_colors if not c.isdigit() and "nocolor" not in c]

    letters_only = re.compile(r"[^a-z]")

    clean_colors = [
        " ".join(re.sub(letters_only, "", t).strip() for t in color.split()).strip()
        for color in clean_colors
    ]
    clean_colors = list(set(clean_colors))
    services.save_json(output_dir / "clean_colors.json", clean_colors)
