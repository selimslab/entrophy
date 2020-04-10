import constants as keys
import data_services
from services import json_util
from supermatch.main import create_matching
from test.test_logs.paths import get_paths
# from test.excel.excel import create_excel
import data_services.mongo.collections as collections
import logging
import sys
from supersync.syncer import strip_debug_fields

def run_matcher(name, links, links_of_products=None):
    query = {keys.LINK: {"$in": links}}
    docs_to_match = data_services.get_docs_to_match(query)

    full_skus = create_matching(
        docs_to_match=docs_to_match, links_of_products=links_of_products
    )

    basic_skus = strip_debug_fields(full_skus)


    paths = get_paths(name)
    # create_excel(cursor=docs, excel_path=paths.excel_path)
    json_util.save_json(paths.full_skus_path, full_skus)
    json_util.save_json(paths.basic_skus_path, basic_skus)


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    links = [
        "https://www.migros.com.tr/sek-sut-200-ml-p-a807b4",
        "sut-urunleri-kahvaltilik/sut-urunleri/sek-sut-200ml-uht-sade",
        "c455e4d8-2a8c-4ff8-a593-860b014e0e12",
        "c5633fd8-bae1-414f-9b92-3e598eaf224c",
        "6b7fd60c-455e-4417-a915-25b0fa4ec881",
        "https://www.carrefoursa.com/tr/sek-sut-200-ml-p-30095209",
        "https://www.groseri.com/urunler/sek-sut-200-ml",
        "https://www.mopas.com.tr/sek-sut-200-ml/p/84300",
        "https://www.google.com/shopping/product/8646735486371191773",
        "451c7c65-fd17-4dab-9d5a-09a4b8c7f39f",
        "9f0fd533-258d-4409-a944-74322fc4818d",
        "https://www.groseri.com.tr/urunler/sek-sut-200-ml",
        "4bcb78d5-4548-4eb7-b4c6-cca1865b7488",
        "267eeacc-ba86-42e1-8e9d-9c0f78425d88",
        "39f2b1ce-8d0e-4188-a862-29e07fe8efdf",
        "https://www.carrefoursa.com/tr/sek-uht-sut-500-ml-p-30095210",
        "https://www.mopas.com.tr/sek-sut-500-ml/p/449825",
        "https://www.google.com/shopping/product/3457435555160574044",
        "https://www.migros.com.tr/sek-sut-500-ml-p-a807aa",
        "sut-urunleri-kahvaltilik/sut-urunleri/sek-sut-500-ml-tam-yagli"
    ]
    run_matcher(name="süt", links=links)
