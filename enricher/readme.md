

## with cat

myo, wat, gratis, c4, ross, ty, migros, joker, civil

## with brand

myo, wat, gratis, c4, ross, ty

## Steps 

* read full skus 
* convert cat to subcat

    Eliminate "ler" "lar" "leri" "ları" at the end of subcat which is from any vendor. "Sıvı Deterjanlar -> Sıvı Deterjan"
    split by / , & 
    
    eg. "Şeker, Tuz, Baharat" ->  [Şeker, Tuz, Baharat]
    
    eg. "bebek bezi/bebek, oyuncak" -> [ bebek bezi, bebek, oyuncak]

* clean names, brands, subcats
    * replace turkish chars 
    * allowed chars are a-z A-Z 0-9 and , . * are, remove all else 
    * remove whitespace
    * only size can have a dot . char, other dots are removed. (-We dont need size for category anymore, after product grouping)


    
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
    * for every subcat, train a different LDA model 
    * a type should be in min. 2 brands, and min. 5 skus 
    

From Zero

Öncelikle temizledeğimiz, karakter değişikliği yaparak “modified” ettiğimizin herşeyin original halini de saklıyoruz.

Veri Temizliği

And, ve, for, için ("and" , "ve" , “for” , “için” tek başına ve iki tarafında space var ise) kelimelerini matching'e özel tek bir format haline getiriyoruz. Matching'de kullanırkan "Head&Shoulders", "Head& Shoulders", "Head &Shoulders", "Head and Shoulders", "Head ve Shoulders" 5'lisi bizim için exact match'tir.
Noktalama işaretlerini temizliyoruz.
1.75L, 1.75 L, 1750ml, 1750 ml, 1750 mililitre ve 1.750ml'in aynı olduğunu anlamak için matching' özel size temizliği yapıyoruz.
Türkçe'ye özel ğ,ü,ş,i,ö,ç harflerini ingilizce karşılıklarıyla hem büyük hem de küçükler için matching'e özel değiştiriyoruz.
“Kg” ya da “KG.” ile biten ve oncesinde bosluklu ya da bosluksuz numeric bir karakter bulunmayan tum itemlardan bu “kg” ve “kg.”leri siliyoruz. 
Item Name sonunda 8, 10, 11 veya 13 karakterli bir numeric var ise, barkod olarak içeri alıp, name’den bu kısmı çıkarıyoruz. 
NOT: Başka sayı temizliği yapmayacağız! Numaralar color ya da size numarası olabilir!
Type’a gelene kadar herhangi ekstra bir temizlik yapmayacağız.
Bu temizlikleridimizi ilerideki aşamalarda item içinde araycağımız “Color” , “Brand” ve “Subcat” içinde yapıyoruz.
Not: Güneş ürünlerinde SPF20, GKF30 gibi önemli ayrıntıların silindiğini gördüm. Veri temizliğinde bu satırlarda stick kalalım.
Matching
1- Barcode Match
2- Exact Name Match
3- Set Match
4- Sponsored Match (Bunu yakın zamanda kaldırmayı planlıyorum, herhangi bir kısmı ya da maintain için ekstra bir emek sarfetmeyelim. Sponsorları bundan sonra daha çok barcode generator olarak kullanacağız.)

Not: 5d7bf018fb73f00e578baf42 skuid’deki gibi ürünlerle karşılaştım. Burada migros ürününü bağlayabileceğimiz iki farklı SKU var (diğeri 5d7bdff4525e36c343df1748), biri sadece google’ın olduğu, diğeri de olağan SKU. Migros item tek google olana bağlanmış. Bu da app’te bu tarz ürünleri only Migros göstermemize neden oluyor. Exact Name Match ve Set Match’te eşitlik halinde google’ın olmadığı item’ı önceliklendirelim. Ya da önce google’ın olmadığı SKU’ları alalım. Ya da son durumda sponsored match ne kadar işimize yarıyor, bir konuşalım, kaldırabiliriz.


Önemli:
En son skuid’yi fixlememiz lazım. Sepete atılan ürünler, geçmiş alışverişler ve recommendation bu id’ler üzerinden çalışacak. Stabil olmalı. Birbiri ile merge eden ürünlerin “or” ile bağlanan 1’den fazla skuid’si olabilir.

Sizing
Halihazırda her item için sizing yapıyoruz. SKU’ları grupladıktan sonra, item’lar içindeki farklı size’lardan en fazla hangisi varsa onu alacağız.

Örnek SKU:
Gliss 525ML
Gliss 550ML
Gliss 525ML
Bu SKU’nun size’ı 525ML’dir.
Bir SKU’ya tek size vereceğiz. Group match’e giderken de item’lardaki bütün size’ları sileceğiz. 
Group match’te SKU’nun size topic’i bu verdiğimiz “tek” size olacak. App’te de variant olarak bunu kullanacağız.

Color
Bize zaten gratis ve TY’den color verisi geliyor. Gelen color verilerini, color’ın geldiği vendor item’ı da dahil olmak üzere, SKU içindeki item’larda arayacağız. Bulduğumuzda o SKU’ya bu color’ı atayacağız. Bir SKU için 1’den fazla color verisi var ise tüm color verilerini arayacağız. 
Veri Temizliği
Bunun aramasını yaparken black=siyah, dark=koyu gibi basit şeylerin TR-EN karşılıklarını da arayalım.

Örnek SKU:
Trendyol	Rimmel London Black		Black (Bu item için TY’den gelen color)
Gratis 	Rimmel London Dark Black	Black (Bu item için Gratis’ten gelen color)
Migros	Rimmel London Koyu Siyah	-	   (Migros’tan gelen color yok)

Öncelikle hem Black’i hem de Dark Black’i bu SKU’nun içindeki item’larda arayıp, color olarak işaretleyip item’lardan çıkaracağız. Sonrasında tüm SKU’lar için geçerli TR-EN ilkel sözlüğümüze bakıp, bu SKU için karşılığını da arayıp (bu case için ayrı ayrı koyu siyah veya siyah), product grouping için tüm color’ları temizliyoruz. 
TR-EN Dictionary’i sadece color verisi geldiyse, karşılığını aramak için kullanıyoruz. Bu renkleri direkt olarak SKU’larda aramıyoruz.
Vendor’dan direkt olarak color verisi gelmedikçe, herhangi bir SKU’ya color atamıyoruz.
Gelen color verisini item içinden silerken, color’a ait tüm token’ları siliyoruz.

Örnek: SKU için gelen color verisi : Red Special Edition
Item Name’lerden biri: “Iphone X Kırmızı Edition”
Burada Kırmızı ve Edition kelimelerini de siliyoruz. Tamamının geçmesini beklemeye gerek yok.

Topic olarak seçeceğimiz ve app’te göstereceğimiz rengi, öncelik sıralamasıyla TY ve Gratis olarak seçelim ve bir tanesini kullanalım. TR-EN dictionary’den topic renk seçmeyeceğiz.

Product Grouping
Burada Set Match’ten color ve sizing’i çıkaracağız ve SKU gruplarını yine ortak set zorunlu olacak ve karakteristik sette de alt küme olacak şekilde birbirleri ile eşleştireceğiz. 
Eşleştirirken önemli olan, bunu sadece 1 SKU’yu başka 1 SKU ile eşleştirmek olmalı, product grouping sadece bir aşama olmalı. Şu anki SKU match’teki gibi bir kısmını gruplayıp daha sonra içini doldurmaya çalışmamalıyız, yoksa tüm brand’i gruplarız.  Fakat aynı SKU da 1’den fazla SKU ile eşleşebilir. En sonunda şöyle bir durum yapacağız:
SKU A is merged with SKU B, SKU D, but not with SKU C
SKU B is merged with SKU C and SKU A
Then SKU A, SKU B, SKU C and SKU D are the same product. 

Şu anki halinde 5d9b1c70de05821195e72b40 skuid dikkatimi çekti. Bu SKU’nun ortak seti “Prima Premium Care”, fakat biz tüm prima’ların içine bunu dahil etmişiz.

Product grouping yaparken hem color hem de size içeren ürünler olması muhtemel. Bu durumda biz grouping’imizde color öncelikli gideceğiz. Eğer color var ise, size üzerinden bir gruplama yapmayacağız.
Örnek:
A: Iphone X 64 GB Black
B: Iphone X 64 GB White
C: Iphone X 128 GB Black
D: Iphone X 128 GB White
Bu case’de A ve B ürünleri beraber bir product oluştururken, C ve D ürünleri de beraber ayrı bir grup oluşturacak. A,B,C,D ürünleri hep beraber bir product oluşturmayacaklar
Fakat bu ürünlerin size’ını 64GB ve 128GB olarak tutmaya devam edeceğiz.

Örnek:
A: Iphone X 256 GB
B: Iphone X 512 GB
Bu case’de color yok. A ve B ürünleri size üzerinden gruplanabilir.

Product Grouping ile işimiz bittiğinde, ne ile grupladıysak o token’ları çıkarıp bir “Product Name” vereceğiz. İlk örnek için Iphone X 64GB ve Iphone X 128GB gibi.


Brand
Verileri temizliyoruz
Vendor’lardan item’lara 1 ya da 1’den fazla brand verisi gelebilir. En çok gelen brand verisini buluyoruz ve item’ların başında arıyoruz. En çok gelen veriyi bulamazsak, ikinci en çok gelen veriyi buluyoruz ve yine item’ların başında arıyoruz. İlk bulduğumuz brand verisini verified brand olarak atiyoruz. Fakat bu sku’ya henuz bir brand vermedik. 
Verified brand’ler icinde, ayni kelime ile baslayip en kisa olan brand’leri buluyoruz. 
Ornek:
Gillette ve Gillette Mach3. Ikiside ayni kelime ile basliyor. Buradaki Gillette Mach3’u Gillette ile degistiriyoruz. 

Sadelestirme islemini item’daki butun marka verilerine uyguluyoruz, ve daha once buldugumuz brand’leri bu degistirilmis brand’ler olarak sku’lara atiyoruz. 
Majority’e bakmadan gördüğümüzde direkt atayacağımız, sadelestirmeden yararlanmayacak olan manuel bir şekilde manuple edeceğimiz birkaç marka var. Loreal Paris bunların ilki. Loreal görünce Loreal Paris’i direkt olarak yapıştırabiliriz. Bunlardan cok az vardir. Gordukce manuel bir sekilde gireriz. 


Subcat
Subcat= İlgili vendor’ın category ağacındaki son eleman.

Bütün vendor’lardan subcat’leri tam ve doğru bir şekilde aldığımıza emin olalım.

Örnek: https://www.migros.com.tr/selin-limon-kolonyasi-900-ml-p-20a3cfb linkinin subcati’ini Kağıt,Kozmetik olarak almışız. Fakat crawl ederken Kağıt, Kozmetik’e girdikten sonra sol taraftaki “kolonya”yı tıklayarak crawl ettik. Bize gelen subcat verisi kolonya olmalı.

Örnek: https://www.trendyol.com/pastel/dudak-parlaticisi-profashion-lip-topper-no-303-shimmering-bronze-8690644003035-p-2037167 linki için “['Kozmetik', 'Makyaj', 'Ruj', 'Dudak Makyajı’]” hiyerarşisiyle almışız. TY’de böyle birşey yok. Bu üründen gelen veri bu: “category":{"id":1156,"name":"Ruj","hierarchy":"Kozmetik & Kişisel Bakım/Makyaj/Dudak Makyajı/Ruj”

Örnek: 5d7bdfa6525e36c343df0d75 https://www.furpa.com.tr/product/ariel-matik-6kg-dag-esintisi-renklilere-ozel/bb92b52e-060f-4b75-a079-632b062fee53 Bu ürün “Toz Deterjan” olarak bitiyor. ['Toz Deterjanlar', 'PG ÜRÜNLERİ'] olarak değil.

TY’deki son eleman = Hiyerarşideki son söz öbeği, Ruj
Migros’taki son eleman, crawl ederken solda tıklanabilir son kategori elemanı, kolonya.

Tüm diğer vendor’lar da yine aynnı şekilde.

Vendor’lardan gelen subcat verilerini “&” ve “,” kısımlarından ayırıyoruz. Bu kısmı “OR/VEYA” bağlacı ile kullanacağız.
Ayırdığımız veriler ile diğer bütün subcat’lerin sonundaki (sadece sonundaki) “ler”, “lar” eklerini siliyoruz. “leri” ve “ları” ile bitenlerden de son 4 harfin ilk 3’ündeki “ler” ve “lar” kısımlarını siliyoruz, son harfi bırakıyoruz.
Örnek:
Unlar & Yumurtalar —> “Un” or “Yumurta”
Unlar Yumurtalar —> “Unlar Yumurta”
Çamaşır Deterjanları —> “Çamaşır Deterjanı”

Vendor’lardan SKU’ya gelen 1’den fazla subcat verisi var elimizde.
İlk olarak yine majority’e bakıp karar veriyoruz. Çoğunluğun kabul ettiği subcat ismi product’ımızın içinde arıyoruz. Varsa subcat tamamdır. Yoksa, ikinci en çok geçeni arıyoruz. Buna bulana kadar devam ediyoruz. Bulamazsak subcat atamıyoruz.

Önemli:
Subcat’lerin modified hali eger baska yerde original ise, bunu kullanacagiz. Yani subcat’te direkt original varsa topic subcat bu olacak
Örnek SKU:
A:Ariel Çamaşır Deterjanı		Migros		Çamaşır Deterjanı
B:Ariel Dağ Çamaşır Deterjanı	Trendyol		Çamaşır Deterjanları
C:Ariel Dağ Esintisi Ç. Deterjanı	Gratis		Çamaşır Deterjanları

B ve C item’ındaki subcat’i temizledik ve “Çamaşır Deterjanı” yaptık. Bu modified subcat’ı tekrardan original’e geçirince, majority’den bu SKU’ya “Çamaşır Deterjanları” demeyelim. Modified hali zaten başka bir vendor’ın original’ı. Direkt bunu kullanalım ve topic yapalım.


Subbrand
Issue’daki haliyle deneyeceğiz.



