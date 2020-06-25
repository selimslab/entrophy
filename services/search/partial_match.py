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
    # TODO simpler
    # diff = []
    tolerate_single_letter = True
    for window_token, needle_token in zip(window_tokens, needle_tokens):
        if window_token == needle_token:
            continue
        else:
            min_token_len = min(len(window_token), len(needle_token))
            if window_token[:min_token_len] == needle_token[:min_token_len]:
                # diff.append((window_token, needle_token))
                #  tolerate max 1 single-letter-token diff
                # Aranan yerde bir harfli olan kelimeyi doldurma toleransımız sadece 1(bir).
                if len(window_token) == 1:
                    if not tolerate_single_letter:
                        return False
                    tolerate_single_letter = False
            else:
                # tokens are different, so does first parts
                return False

    return True


def partial_string_search(haystack: str, needle: str) -> Union[str, None]:
    """
    needle is a full string,
    haystack might contain a corrupted version of it

    as long as there is a substring with
    1. the same number of tokens,
    2. all tokens starting with the same letter
    3. they are in the same order
    4. they have at least 1 common token with len>4
    """
    if needle in haystack:
        return needle

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
        if is_eligible_tokensets(window_tokens, needle_tokens):
            is_found = compare_tokensets(window_tokens, needle_tokens)
            # print(window_tokens, needle_tokens, is_found)
            if is_found:
                # return the similar window
                return " ".join(window_tokens)


def pre_test_match_partially():
    test_cases = [
        ("Garnier Micellar M Tem Suyu", "Makyaj Temizleme Suyu", "M Tem Suyu"),
        ("dadad L Paris asfasfas", "Loreal Paris", "L Paris"),
        ("fasfsa T kağıdı aasda", "Tuvalet Kağıdı", "T kagidi"),
        ("423 Tuv Kağıdı 545745", "Tuvalet Kağıdı", "tuv kagidi"),
        ("Sıvı B Deterjan", "Sıvı Bulaşık Deterjanı ", "sivi b deterjan"),
    ]
    for (haystack, needle, expected) in test_cases:
        res = partial_string_search(
            services.clean_string(haystack), services.clean_string(needle)
        )
        try:
            assert res == expected.lower()
        except AssertionError:
            print(haystack, needle, expected, res)


if __name__ == "__main__":
    pre_test_match_partially()
