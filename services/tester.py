def check(func, test_cases):
    fail = False
    for case in test_cases:
        *args, expected = case
        res = func(*args)
        try:
            assert res == expected
        except AssertionError as e:
            print()
            print(f"FAIL for {args}")
            print(f"expected {expected}")
            print(f"got {res}")
            print(e)
            fail = True
    if fail:
        raise AssertionError
