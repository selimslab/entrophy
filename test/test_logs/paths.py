import os
from dataclasses import dataclass
import pathlib


def get_paths(name):
    cwd = pathlib.Path.cwd()
    target = cwd / name
    if not os.path.exists(target):
        os.makedirs(target)

    @dataclass
    class Paths:
        full_skus = target / "full_skus.json"
        basic_skus = target / "basic_skus.json"
        docs = target / "docs.json"
        excel = target / "rows.xlsx"

    return Paths
