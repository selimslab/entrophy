from data_services.mongo.collections import test_collection, items_collection
import api.sentry
import constants as keys


"""
            {
                "$project ": {
                    # "_id": 0,
                    keys.LINK: 1,
                    keys.BARCODES: 1,
                    keys.PROMOTED: 1,
                    keys.VARIANTS: 1,
                    keys.VARIANT_NAME: 1,
                    keys.SKU_ID: 1
                }
            },
"""
if __name__ == "__main__":
    items_collection.aggregate(
        [
            {'$match': {}},
            {'$out': 'items_backup'}
        ]
    )
