import pathlib
import services
from test.paths import get_path

cwd = pathlib.Path.cwd()
test_logs_dir = cwd / "test_logs"

if __name__ == "__main__":
    full_skus_path = get_path("may18/full_skus.json")
    print(full_skus_path)
