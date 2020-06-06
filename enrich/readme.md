## Steps 

* read full skus 
* convert cat to subcat -> "bebek bezi/bebek, oyuncak" -> bebek bezi
* clean names, brands, subcats
    * replace turkish chars 
    * allowed chars are a-z A-Z 0-9 and , . * are, remove all else 
    * remove whitespace
    * only size can have a dot . char, other dots are removed 


    
+ create brand_subcats_pairs
        
    "ariel": [
        "sivi jel deterjan",
        "matik deterjanlar",
        "camasir yikama urunleri",
        "camasir leke cikarici",
        "anne bebek bakim",
        ...
    ]
    
    "nestle": [
        "kahve kremasi",
        "krem cikolata ezme",
        "toz icecek",
        "krem cikolata ve ezme",
        "saglikli yasam urunleri",
        "kahve",
        "gida icecek",
        "cikolata",
        "hediyelik cikolata",
        "cikolatalar barlar gofretler",
        "icecek tozu",
        ...
    ]
    
    
+ create clean_brand_original_brand_pairs

    "uludag": "Uludağ",
    "nestle": "Nestle",
    "sirma": "Sırma",
    "pinar": "Pınar" 
    ...
    
    
+ find the term frequencies of first two tokens in all names, add to the brand pool if freq > 60 

+ for every sku, for every name, search the brands in brand_pool in the first 4 tokens of the name 

+ for every sku, create possible subcat space
    * add subcats in sku, if they are in any of the names
    * add possible_subcats_for_this_brand
    * add possible_subcats_for_this_brands_root_brand 
    * eg. if brand is eti hosbes, possible subcats of both eti, and eti hosbes are considered 
    * deduplicate and remove very long sub_cats (len>30), they are mostly wrong, remove if a subcat is also in the brand pool 


+ create sub_cat_market_pairs

    "zeytinyagi": [
        "rammar",
        "yunus",
        "ty",
        "carrefoursa"
    ],
    
  
+ select a subcat 
    * sort possible subcats by length
    * start from the longest, prioritize by [keys.TRENDYOL, keys.GRATIS, keys.WATSONS, keys.MIGROS] 
    * if the subcat belongs to any of, select it 
    * at the and, if none of them is selected, select the longest 

+ at this point, we have docs with brands and subcats 

    {
        "brand": "prima aktif",
        "subcat": "bebek bezi",
        "names": [
            "prima aktif bebek mega firsat paketi 5 beden 62 adet",
            "prima mega firsat paketi 5 numara junior 62 adet",
            "prima aktif bebek bezi 5 beden junior mega firsat paketi 62 adet"
        ]
    },
    {
        "brand": "heinz ketcap",
        "subcat": "ketcap",
        "names": [
            "heinz ketcap 700 gr"
        ]
    },


+ for topic modelling
    * remove subcats and brands from names
    * -> we may also remove barcodes, all sizes, maybe even gender, color
    * join all names in an sku so a sku is the smallest unit of the model 
    * for every subcat, train a different LDA model 
    


