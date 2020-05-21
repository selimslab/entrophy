from typing import List

from .barcode_cleaner import *
from .convertor import *
from .generic_graph import *
from .get_soup import *
from .json_util import *
from .name_cleaner import *
from .token_util import *
from .collections_util import *


def clean_list_of_strings(l: List[str]):
    return [clean_name(x) for x in l]


def clean_list_of_strings_and_remove_nulls(l: List[str]):
    return remove_null_from_list(clean_list_of_strings(l))
