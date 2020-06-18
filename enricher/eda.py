import logging
from typing import List

import services
import constants as keys
from paths import output_dir


def eda():
    with_brand_only = services.save_json(output_dir / "with_brand_only.json")


if __name__ == "__main__":
    eda()
