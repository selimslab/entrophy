def string_to_extending_windows(s: str, end: int = None) -> list:
    """
    "a b c" -> [ a, ab, abc ]
    """
    tokens = s.split()
    if not end:
        end = len(tokens)
    return [" ".join(tokens[:i]) for i in range(1, end + 1)]
