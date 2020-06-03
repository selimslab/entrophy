from pprint import pprint


class Trie:
    """ or prefix tree """

    def __init__(self):
        """
        a child of a Trie is a Trie
        """
        self.trie = {}

    def __repr__(self):
        pprint(self.trie)

    def insert(self, tokens: list) -> None:
        """
        Inserts a word into the trie.
        """
        t = self.trie
        for token in tokens:
            if token not in t:
                t[token] = {}
            t = t[token]


def test_trie():
    trie = Trie()
    names = [
        "loreal paris revitalift yaslanma karsiti",
        "loreal paris ruj color riche",
        "nyx professional makeup slim eye",
        "nyx professional makeup slim lip",
    ]
    for name in names:
        tokens = name.split()
        trie.insert(tokens)

    print(trie)


test_trie()
