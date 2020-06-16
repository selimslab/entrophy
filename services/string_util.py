from services.tester import check

def get_all_contigious_substrings_of_a_string(s: str):
    tokens = s.split()
    n = len(tokens)
    substrings = []
    for start in range(n):
        for end in range(1, n + 1):
            word_group = " ".join(tokens[start:end])
            if word_group:
                substrings.append(word_group)
    return substrings


def test_get_all_contigious_substrings_of_a_string():
    cases = [
        ("a b c", ['a', 'a b', 'a b c', 'b', 'b c', 'c'])
    ]

    check(get_all_contigious_substrings_of_a_string, cases)