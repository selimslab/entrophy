from typing import Union

from services import flattener


class BarcodeCleaner:
    @staticmethod
    def get_tokens(barcodes: Union[list, str]) -> list:
        if not isinstance(barcodes, list):
            barcodes = barcodes.split(",")
        tokens = [token.split(",") for token in barcodes]
        tokens = flattener.flatten(tokens)
        tokens = [token.strip() for token in tokens]
        return tokens

    @staticmethod
    def get_google_barcodes_from_info(info):
        tokens = BarcodeCleaner.get_tokens(info)

        tokens = [
            token.lstrip("0")
            for token in tokens
            if len(token) == 13 or (len(token) == 14 and str(token[0]) == "0")
        ]

        google_barcodes = [t for t in tokens if t.isdigit()]

        return list(set(google_barcodes))

    @staticmethod
    def get_clean_barcodes(barcodes):
        # "42424,4234324" -> ["42424,4234324"] -> ["42424", "4234324"]
        tokens = BarcodeCleaner.get_tokens(barcodes)
        b8_13 = [token for token in tokens if len(token) in {8, 13}]
        b14 = [
            token[1:]
            for token in tokens
            if len(token) == 14 and str(token[0]) == "0" and str(token[1]) != "0"
        ]
        clean_barcodes = [b for b in b8_13 + b14 if b.isdigit()]

        return list(set(clean_barcodes))


if __name__ == "__main__":
    print(
        BarcodeCleaner.get_clean_barcodes(
            [
                "2009994000001"
            ]  # "4242424242425,08242424242425, 00000012345678, 8690710140022"
        )
    )
    print(BarcodeCleaner.get_clean_barcodes("4242424242425"))
