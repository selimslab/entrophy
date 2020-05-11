"""

1- Brand Identity
a- Brand Name (GTIN ile zorunlu)
Genellikle ismin başında geçen unique kelime(ler). GTIN'i olan bütün ürünlerin Brand Name'i olmak zorundadır.
b- Sub-Brand Name
Brand'in alt kümesi olan, ürün ismi içinde yeri değişken olabilen brand'e özgü kelime ya da tekrar eden kelimeler.

2- Market Spesifics
a- Sub-Category (Zorunlu)
Maksimum ürünü, minimum kelime sayısı ile anlatan kelime ya da tekrar eden kelimeler, en büyük cluster. İsminde geçmese bile, bir ürünün sub-category'si olması zorunludur.
b- Type
Sub-category içindeki tüm ürünleri, minimum cluster'a ayırabildiğin kelime ya da tekrar eden kelimeler. 1'den fazla brand'in ürününde geçmek zorundadır.
c- Other Variants
Bunlar tamamen sub-category'e özgü değişen, 1'den fazla brand'de bulunmak zorunda olan, sub-category'deki ürünlerin bir kısmında bulunup diğer kısmında bulunmayabilen, ama sub-category'nin azınlık olmayan bir kısmını define edebilen kelime ya da tekrar eden kelimelerdir.

3- Universal
Bunlar sub-category ve/veya category'e özgü (ayakkabi için size 40,41,etc, category'e özgüdür, fakat şimdilik çektiğimiz yerlerde ürün isminde geçmediği için ignore edebilirz) olabilir ya da olmayabilir (gr, ml universal'dır).
a- Size
Bunun için bir modellemeye ihtiyaç yok. Ölçü birimleri gayet net. Given verilebilir şeylerden oluşuyor. (Alphanumeric: gr, ml, yıkama, adet, GB, TB, MB (Byte group) Alpha: XXXS-XXS-XS-S-M-L-XL-XXL-XXXL-XXXXL...) Bazı ürün gruplarında 1'den fazla aynı ölçü birimi olabilir "MacBook 1TB SSD 8GB RAM". Bu nedenle şimdilik iki tane varsa büyük olanı doğru yapıp, ileride category'e özgü size çalışabiliriz.
b- Gender
Modele gerek yok. Bu kısım tamamıyla universal ve given'dır.
Erkek = Bay, Men, Man
Kadin = Bayan, Women, Woman
Bebek = Bebe, Baby
c- Colors
Tamamen universal'dır. İngilizce ve Türkçe değişebilir.
Given olarak verilecektir ((light or dark) red)).
Veri çektiğimiz yerlerden renkleri her category için ayrı şekilde saklayacağız ve arayacağız.
"""

"""
steps 

1. clean()

2. match_groups()
"""
