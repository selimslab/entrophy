from .barcode_matcher import BarcodeMatcherMixin
from .exact_name_matcher import ExactNameMatcherMixin
from .promoted_link_matcher import PromotedLinkMatcherMixin


class Matcher(ExactNameMatcherMixin, BarcodeMatcherMixin, PromotedLinkMatcherMixin):
    pass
