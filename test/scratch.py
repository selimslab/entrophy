def update(d: dict):
    d[3] = 5


def test_dict_update():
    """ variable as pointers to boxes """
    d = {3: {2: 4}, 4: {}}
    update(d)
    print(d)
