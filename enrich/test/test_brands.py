import services
import constants as keys
from paths import input_dir, output_dir
from collections import Counter, OrderedDict


def test_brands():
    skus = services.read_json(input_dir / "full_skus.json").values()
    names = [sku.get(keys.CLEAN_NAMES, []) for sku in skus]
    token_lists = services.get_token_lists(names)
    first_n_tokens = [" ".join(tokens[0:5]) for tokens in token_lists]
    filtered_tokens = [token for token in first_n_tokens if len(token) > 2]
    freq = OrderedDict(Counter(filtered_tokens).most_common())
    services.save_json(output_dir / "name_freq_first_5.json", freq)


if __name__ == "__main__":
    ...
