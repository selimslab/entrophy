from dataclasses import dataclass, field


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


if __name__ == "__main__":
    bar()
