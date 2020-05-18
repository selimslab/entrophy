import services


def tokenize(s: str):
    if s and isinstance(s, str):
        return [t.strip() for t in s.split()]


def get_tokens_of_a_nested_list(l: list):
    l = services.flatten(l)
    strings = [s for s in l if isinstance(s, str)]
    tokens_list = [tokenize(s) for s in strings]
    tokens = services.flatten(tokens_list)
    return tokens


def get_cleaned_tokens_of_a_nested_list(l: list):
    tokens = get_tokens_of_a_nested_list(l)
    return services.clean_list_of_strings(tokens)


def test_get_tokens_of_a_group():
    x = get_tokens_of_a_nested_list(["quick fox", "lazy dog"])
    assert set(x) == {"quick", "fox", "lazy", "dog"}
    y = get_tokens_of_a_nested_list([{"quick fox"}, "lazy dog"])
    assert set(y) == {"lazy", "dog"}


if __name__ == "__main__":
    pass
