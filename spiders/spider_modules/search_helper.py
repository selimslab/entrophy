import constants as keys
import data_services.mongo.collections as collections

CUSTOM_SEARCHBOX_SETTINGS = {
    "DOWNLOAD_DELAY": 2,
    "ITEM_PIPELINES": {"src.spiders.pipelines.search_pipeline.SearchPipeline": 300},
}


class BarcodeSearchHelper:
    @staticmethod
    def barcode_generator(barcodes_to_search):
        for barcode in barcodes_to_search:
            if str(barcode[0]) == "0":
                if len(barcode) == 8:
                    continue
                if len(barcode) == 14:
                    if str(barcode[1]) == "0":
                        continue
                    else:
                        barcode = barcode[1:]
                else:
                    continue

            yield barcode

    @staticmethod
    def get_barcodes_to_search(market_name, market_list):
        all_barcodes = collections.items_collection.distinct(
            keys.BARCODES, {keys.MARKET: {"$in": market_list}}
        )
        return all_barcodes
