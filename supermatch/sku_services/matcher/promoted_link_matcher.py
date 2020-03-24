import constants as keys


class PromotedLinkMatcherMixin:
    @staticmethod
    def get_promoted_links(promoted: dict) -> list:
        promoted_links = []
        for promoted_name, link in promoted.items():
            if any(
                [
                    market_name in promoted_name
                    for market_name in keys.ALLOWED_MARKET_LINKS
                ]
            ):
                if link[-1] == "/":
                    link = link[:-1]

                if "&gclid" in link:
                    link = link.split("&gclid")[0]
                if "?gclid" in link:
                    link = link.split("?gclid")[0]
                if "?utm" in link:
                    link = link.split("?utm")[0]
                if "&utm" in link:
                    link = link.split("&utm")[0]

                link = link.strip()
                promoted_links.append(link)

        return promoted_links

    @staticmethod
    def create_link_id_pairs(id_doc_pairs) -> dict:
        link_id_pairs = dict()
        for doc_id, doc in id_doc_pairs.items():
            link_id_pairs[doc.get(keys.LINK)] = doc_id
        return link_id_pairs
