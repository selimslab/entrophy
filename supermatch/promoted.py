import constants as keys
import services
from tqdm import tqdm


def clean_promoted_link(promoted_name, link):
    if any([market_name in promoted_name for market_name in keys.ALLOWED_MARKET_LINKS]):
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
        return link


def get_promoted_links(promoted: dict) -> list:
    promoted_links = [
        clean_promoted_link(promoted_name, link)
        for promoted_name, link in promoted.items()
    ]

    promoted_links = services.remove_null_from_list(promoted_links)

    return promoted_links


def promoted_match(self):
    link_id_pairs = dict()
    for doc_id, doc in self.id_doc_pairs.items():
        link_id_pairs[doc.get(keys.LINK)] = doc_id

    promoted_connections = dict()
    refers_to_multiple_barcodes = set()

    for doc_id, doc in tqdm(self.id_doc_pairs.items()):
        promoted = doc.get(keys.PROMOTED, {})
        if not promoted:
            continue
        promoted_links = get_promoted_links(promoted)
        promoted_links = [link for link in promoted_links if link in link_id_pairs]

        # add edge iff sizes are the same
        referenced_ids = [link_id_pairs.get(link) for link in promoted_links]

        # promoted link artık sadece barcode u olmayanları bir gruba bağlıyor
        filtered_referenced_ids = [
            id
            for id in referenced_ids
            if not self.id_doc_pairs.get(id, {}).get(keys.BARCODES)
        ]

        # bir linki birden fazla link promote ediyorsa, hiçbiri dikkate alınmıyor
        for id in filtered_referenced_ids:
            if id in promoted_connections:
                refers_to_multiple_barcodes.add(id)
            else:
                promoted_connections[id] = doc_id

    promoted_connections = {
        id: doc_id
        for id, doc_id in promoted_connections.items()
        if id not in refers_to_multiple_barcodes and id not in self.connected_ids
    }

    for id, doc_id in promoted_connections.items():
        self.sku_graph.add_edge(id, doc_id)
        self.connected_ids.add(id)
        self.stages[id] = "promoted"
