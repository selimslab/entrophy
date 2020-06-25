from collections import Counter, defaultdict
import services
import constants as keys


def get_inverted_token_index(subcats_assigned):
    inverted_index = defaultdict(set)
    tokensets = {}
    for sub in subcats_assigned:
        tokens = sub.split()
        if len(tokens) == 1:
            continue
        tokensets[sub] = set(tokens)
        for token in tokens:
            inverted_index[token].add(sub)

    return inverted_index, tokensets


def init_merged_subcats(sub_count: dict):
    """
    1- Modified halleri ile sadece son 3 harfleri farklı olan,
    7 harften büyük subcat'leri, büyük olana merge ediyoruz.

    Örnek: "Camasir Suyu" ve "Camasir Su" merge edip, "Camasir Suyu" haline getiriyoruz.
    Topic olarak kullanmak üzere original halini tutmaya devam ediyoruz.

    """
    merged_subcats = {}

    for sub in sub_count:
        if len(sub) <= 7:
            continue
        for other_sub in sub_count:
            if len(other_sub) <= len(sub) or len(other_sub) - len(sub) > 3:
                continue
            if sub == other_sub[: len(sub)]:
                merged_subcats[sub] = other_sub
                break

    return merged_subcats


def get_subsets(sub, inverted_index, tokensets):
    """
    2- Token olarak birbirinin içinde geçen ve 1'den fazla kelime içeren subcat'leri kısa olanın içine dahil ediyoruz.

     (Tek kelimeli subcat'ler kesinlikle bu sürece dahil olmayacak)

     Örnek: A: "Sıvı ve Jel Çamaşır Deterjanı" ve B:"Sıvı Deterjanı" B'nin tüm token'ları A'nın içinde geçtiği için, A'yı B'ye dahil edip, B'yi topic olarak kullanıyoruz.

    """
    tokens = set(sub.split())
    if len(tokens) == 1:
        return
    subsets = []
    for token in tokens:
        neighbors = inverted_index.get(token, set())
        for n in neighbors:
            if n == sub:
                continue

            if tokens.issuperset(tokensets.get(n, set())):
                subsets.append(n)
    return subsets


def get_sub_count(products):
    all_clean_subcats = []
    for product in products:
        subcats = product.get(keys.SUB_CATEGORIES, [])
        for sub in subcats:
            clean_sub = services.clean_string(sub)
            clean_sub = services.plural_to_singular(clean_sub)
            all_clean_subcats.append(clean_sub)

    sub_count = Counter(all_clean_subcats)
    return sub_count


def get_merged_subcats(products):
    """
    Öncelikle subcat merge'ü ML' girmeden önceki aşamada kullanacağız.

    1- Modified halleri ile sadece son 3 harfleri farklı olan, 7 harften büyük subcat'leri, büyük olana merge ediyoruz. Örnek: "Camasir Suyu" ve "Camasir Su" merge edip, "Camasir Suyu" haline getiriyoruz. Topic olarak kullanmak üzere original halini tutmaya devam ediyoruz.

    2- Token olarak birbirinin içinde geçen ve 1'den fazla kelime içeren subcat'leri kısa olanın içine dahil ediyoruz. (Tek kelimeli subcat'ler kesinlikle bu sürece dahil olmayacak) Örnek: A: "Sıvı ve Jel Çamaşır Deterjanı" ve B:"Sıvı Deterjanı" B'nin tüm token'ları A'nın içinde geçtiği için, A'yı B'ye dahil edip, B'yi topic olarak kullanıyoruz.

    Önceliklendirme: Yukarıya C: "Çamaşır Deterjanı" ekleyelim. Eğer C'nin sahip olduğu product sayısı B'den fazla ise, C hem A'yı, hem de C'nın alt kümesi olduğundan dolayı B'yi kendi içine alır. Eğer B, C'den daha çok ürüne sahip olsaydı, bu 3 subcat'i B'nin içinde merge edecektik.

    """
    sub_count = get_sub_count(products)

    merged_subcats = init_merged_subcats(sub_count)
    inverted_index, tokensets = get_inverted_token_index(sub_count)
    # merge to more frequent one
    # eg. a:3 b:5
    # "a b c" -> b
    # 2- Token olarak birbirinin içinde geçen ve 1'den fazla kelime içeren subcat'leri kısa olanın içine dahil ediyoruz. (Tek kelimeli subcat'ler kesinlikle bu sürece dahil olmayacak) Örnek: A: "Sıvı ve Jel Çamaşır Deterjanı" ve B:"Sıvı Deterjanı" B'nin tüm token'ları A'nın içinde geçtiği için, A'yı B'ye dahil edip, B'yi topic olarak kullanıyoruz.
    for sub in sub_count:
        subsets = get_subsets(sub, inverted_index, tokensets)
        if subsets:
            subset_counts = {s: sub_count.get(s) for s in subsets}
            root_sub = services.get_most_frequent_key(subset_counts)
            merged_subcats[sub] = root_sub

    return merged_subcats
