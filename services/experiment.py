def foo():
    x = set()

    def bar():
        x.add(3)

    bar()
    return x


print(foo())
