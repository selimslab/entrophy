import os
from dataclasses import dataclass


def get_paths(dirname):
    basedir = os.path.dirname(__file__)
    files_dir = os.path.join(basedir, dirname)
    if not os.path.exists(files_dir):
        os.makedirs(files_dir)

    @dataclass
    class Paths:
        id_doc_pairs_path = os.path.join(files_dir, "id_doc_pairs.json")
        skus_path = os.path.join(files_dir, "skus.json")
        products_path = os.path.join(files_dir, "products.json")
        excel_path = os.path.join(files_dir, dirname + ".xlsx")
        config_path = os.path.join(files_dir, "config.txt")
        full_docs_path = os.path.join(files_dir, "docs.json")

    return Paths
