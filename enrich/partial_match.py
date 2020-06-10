from typing import Union
import services


def is_eligible_tokensets(window_tokens: list, needle_tokens: list) -> bool:
    if len(window_tokens) != len(needle_tokens):
        return False
    # Aranacak olan token'ın en az 1 kelimesi, aranan yerde geçmeli
    commonset = set(needle_tokens).intersection(window_tokens)
    if len(commonset) < 1:
        return False
    # Icinde tam olarak gececek kelime minimum 4 harfli olmali.
    if len(commonset) == 1 and len(commonset.pop()) < 4:
        return False

    return True


def compare_tokensets(window_tokens: list, needle_tokens: list) -> bool:
    diff = []
    tolerate_single_letter = True
    for window_token, needle_token in zip(window_tokens, needle_tokens):
        print("diff", diff)
        if window_token == needle_token:
            continue
        elif window_token[0] == needle_token[0]:
            diff.append((window_token, needle_token))
            #  tolerate max 1 single-letter-token diff
            # Aranan yerde bir harfli olan kelimeyi doldurma toleransımız sadece 1(bir).
            if len(window_token) == 1:
                if not tolerate_single_letter:
                    return False
                tolerate_single_letter = False
        else:
            # tokens are different, so does first letters
            return False

    return True


def partial_string_search(haystack: str, needle: str) -> Union[str, None, bool]:
    """
    as long as there is a substring with
    1. the same number of tokens,
    2. all tokens starting with the same letter
    3. they are in the same order
    4. they have at least 1 common token with len>4
    """
    needle_tokens = needle.split()

    #  Aranacak olan subcat, brand vs. 2 ve daha fazla kelimeli olmalı.
    #  Örnek: Loreal Paris, Tuvalet Kağıdı
    if len(needle_tokens) < 2:
        return

    haystack_tokens = haystack.split()

    n = len(needle_tokens)
    # iterate over windows of the size of needle
    for start in range(len(haystack_tokens) - n + 1):
        # Aranacak olan token, aranan yerde aynı sıralama ile geçmeli.
        # this windowing strategy ensures the order
        window_tokens = haystack_tokens[start : start + n]
        print()
        print(needle_tokens, window_tokens)
        # found
        if window_tokens == needle_tokens:
            return True

        ok = is_eligible_tokensets(window_tokens, needle_tokens)
        if ok:
            is_found = compare_tokensets(window_tokens, needle_tokens)
            if is_found:
                return True

    return False


def pre_test_match_partially():
    test_cases = [
        ("Garnier Micellar M Tem Suyu", "Makyaj Temizleme Suyu", True),
        ("dadad L Paris asfasfas", "Loreal Pari", False),
        ("fasfsa T kağıdı aasda", "Tuvalet Kağıdı", True),
        ("423 Tuv Kağıdı 545745", "Tuvalet Kağıdı", True),
        (" Sıvı Bulaşık Deterjanı ", "Sıvı B Deterjan", True),
    ]
    for case in test_cases:
        (haystack, needle) = services.clean_list_of_strings(list(case[:2]))
        expected = case[2]
        try:
            is_found = partial_string_search(haystack, needle) == expected
            print(haystack, needle, is_found)
            assert is_found
        except AssertionError as e:
            print(e)


pre_test_match_partially()
