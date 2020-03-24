import constants as keys


class BarcodeMatcherMixin:
    @staticmethod
    def create_barcode_id_pairs(id_doc_pairs):
        barcode_id_pairs = dict()
        for doc_id, doc in id_doc_pairs.items():
            barcodes = doc.get(keys.BARCODES, [])
            if not barcodes:
                continue

            market = doc.get(keys.MARKET)
            if market in {keys.GOOGLE}:
                pass

            for code in barcodes:
                barcode_id_pairs[code] = barcode_id_pairs.get(code, []) + [doc_id]

        return barcode_id_pairs
