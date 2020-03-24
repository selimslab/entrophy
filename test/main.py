from pprint import pprint

import constants as keys
import data_services
import data_services.mongo.collections as collections


def ask(collection, query):
    cursor = collection.find(query)
    print(collection.count_documents(query))
    for doc in cursor[:10]:
        pprint(doc)


def inspect_case(link):
    query = {keys.LINK: link}

    doc = collections.items_collection.find_one(query)
    pprint(doc)
    if not doc:
        return

    sku_id = doc.get(keys.SKU_ID)
    product_id = doc.get(keys.PRODUCT_ID)
    name = doc.get(keys.NAME)

    print(name, sku_id, product_id)

    print("PRODUCT")
    data_services.search_elastic(name)

    print("SKU")
    data_services.search_in_firestore(sku_id)

    if product_id:
        data_services.search_elastic_by_ids([product_id])
        ask(collections.products_collection, {keys.objectID: product_id})


def get_links_of_a_product(product_id):
    links = collections.items_collection.find(
        {keys.objectID: product_id}, {"_id": 0, keys.LINK: 1}
    )
    links = list(links)
    pprint(links)
    return links


def old():
    link = "9e3ac092-c552-4ca2-b866-f8c5bce05f19"
    link = "https://www.a101.com.tr/market/milka-bonibon-draje-cikolata-3x243-g/"
    link = "https://www.gratis.com/nivea-canlandirici-yuz-yikama-kopugu-150-ml/urun/10013175"
    link = (
        "https://www.cosmetica.com.tr/toni-guy-men-sampuan-yogun-arindirici-250-ml.html"
    )
    # inspect_case(link)
    data_services.search_elastic("toni guy arındırıcı")
    product_id = "5d7be09143a5a28ff82323cb"
    ask(collections.products_collection, {keys.objectID: product_id})
    get_links_of_a_product(product_id)

    pid = "5d7bf00cfb73f00e578ba67e"
    vars = [
        "5d7bf00cfb73f00e578ba6ba",
        "5d7bf00cfb73f00e578ba6bb",
        "5d7bf00cfb73f00e578ba67e",
    ]
    for var in vars:
        data_services.search_in_firestore(var)

    ask(
        collections.items_collection,
        {keys.LINK: "https://www.migros.com.tr/dogus-toz-seker-5-kg-p-3285bd"},
    )


if __name__ == "__main__":
    # data_services.search_barcode(["8690767675089", "8690624101874"])
    # data_services.search_elastic("şampuan")

    """
    ABSENT IN DB
        link = "https://www.carrefoursa.com/tr/pritt-yapistirici-22-g-p-30090339" 
        
    IN DB, NOT IN APP

    
    NO PROBLEM 
        link = "https://www.a101.com.tr/ev-yasam/plastik-bardak-25-li/"
    link = "https://www.a101.com.tr/kozmetik-kisisel-bakim/ipana-pro-white-pearl-glow-dis-macunu-75-ml/"

    """

    # link = "https://www.ceptesok.com/yaban-gulu-yuzey-temizleyici-25-lt"
    link = "https://www.carrefoursa.com/tr/tadim-hurma-163-g-p-30218230"
    link = "https://www.carrefoursa.com/tr/tadim-guneste-kurutulmus-kayisi-140-g-p-30240411"
    ask(
        collections.items_collection, {keys.LINK: link},
    )

    # data_services.search_elastic("Dixi Yüzey Temizleyici")
