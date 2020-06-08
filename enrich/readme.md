## Steps 

* read full skus 
* convert cat to subcat

    split by / , & 
    
    eg. "Şeker, Tuz, Baharat" ->  [Şeker, Tuz, Baharat]
    
    eg. "bebek bezi/bebek, oyuncak" -> [ bebek bezi, bebek, oyuncak]

* clean names, brands, subcats
    * replace turkish chars 
    * allowed chars are a-z A-Z 0-9 and , . * are, remove all else 
    * remove whitespace
    * only size can have a dot . char, other dots are removed 


    
+ create brand_subcats_pairs
  ```
      "ariel": [
        "sivi jel deterjan",
        "matik deterjanlar",
        "camasir yikama urunleri",
        "camasir leke cikarici",
        "anne bebek bakim",
        ...
    ]
  ```


 
+ create clean_brand_original_brand_pairs

    "uludag": "Uludağ",
    "nestle": "Nestle",
    "sirma": "Sırma",
    "pinar": "Pınar" 
    ...
    
+ count brand frequencies only for the brands given by vendors 
   
+ find the term frequencies of first two tokens in all names (-2 kelimeden fazla olan isimlerin içinde arayalım), add to the brand pool if freq > 60 

+ create brand candidates
    for every sku, for every name, search the brands in brand_pool in the first 4 tokens of the name 

+ among the brand candidates, select the most frequent one as brand and the longest one as subbrand 

    idea: Brand correction
   
+ for every sku, create possible subcat space

    * add subcats in sku, if they are in any of the names
    * add possible_subcats_for_this_brand
    * add possible_subcats_for_this_brands_root_brand 
    * eg. if brand is eti hosbes, possible subcats of both eti, and eti hosbes are considered 
    * deduplicate and remove very long sub_cats (len>30), they are mostly wrong, remove if a subcat is also in the brand pool 


+ create sub_cat_market_pairs

-- Buradaki tam amacımız nedir? Bu subcat'ler birçok yerde geçince verified subcat falan mı oluyo?

++ amaç subcat seçerken markete göre önceliklendirebilmek 

    "zeytinyagi": [
        "rammar",
        "yunus",
        "ty",
        "carrefoursa"
    ],
    
  
+ create subcat candidates by searching in names 

+ select a subcat 
    * sort possible subcats by length
    * start from the longest, prioritize by [keys.TRENDYOL, keys.GRATIS, keys.WATSONS, keys.MIGROS] 
    * if the subcat belongs to any of, select it 
    * at the and, if none of them is selected, select the longest 


+ at this point, we have docs with brands and subcats 

```json
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
```



+ for topic modelling
    * remove any subcat, brand, all detected sizes, all-digit tokens from names
    * join all names in an sku so a sku is the smallest unit of the model 
    idea: Buraya sku'lar ile değil de product group ile girsek mantıklı olmaz mı
    * for every subcat, train a different LDA model 
    
Devam edeceğim.



