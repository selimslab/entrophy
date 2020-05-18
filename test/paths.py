import os
from dataclasses import dataclass
import pathlib

cwd = pathlib.Path.cwd()
test_logs_dir = cwd / "test_logs"


def get_path(file_name):
    return test_logs_dir / file_name


def get_paths_in_a_dir(name):
    target_dir = test_logs_dir / name
    print(cwd, target_dir)
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    @dataclass
    class Paths:
        full_skus = target_dir / "full_skus.json"
        basic_skus = target_dir / "basic_skus.json"
        docs = target_dir / "docs.json"
        excel = target_dir / "rows.xlsx"
        processed_docs = target_dir / "processed_docs.json"

    return Paths
