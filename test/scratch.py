from dataclasses import dataclass, field
import itertools


@dataclass
class C:
    a: float
    b: float
    c: []

    def __post_init__(self):
        self.c = [c for c in self.c if c]


x = C(a=3, b=4, c=[0, 7, 3])

print(x)


def foo(d, l):
    d[3][2] = 8
    l.append(4)
    l = [i for i in range(2)]


def bar():
    d = {3: {2: 4}}
    l = [6]
    foo(d, l)
    print(d, l)


d = {3: {2: 4}, 4: {}}


def x():
    for k, v in d.items():
        v.update({2: 7})
    print(d)


def barz():
    x = set()

    def bar():
        x.add(3)

    bar()
    return x



if __name__ == "__main__":
    res = itertools.islice(d.items(), 1)
    print(dict(res))
