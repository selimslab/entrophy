import traceback

from pymongo.errors import PyMongoError

import constants as keys
import data_services.mongo.collections as collections
from data_services import MongoSync
from services.ses import send_email

from tqdm import tqdm


def backup_decorator(func):
    try:
        func()
    except (
        PyMongoError,
        KeyError,
        ValueError,
        TypeError,
        IndexError,
        AttributeError,
    ) as e:
        print(e)
        print(traceback.format_exc())
        try:
            report = "\n\n".join([str(e), str(traceback.format_exc())])
            send_email("backup error", report)
        except (TypeError, AttributeError, KeyError, ValueError) as e:
            print(e)


@backup_decorator
def backup_items_collection():
    print("backing up items_collection..")

    item_cursor = collections.items_collection.find(
        {},
        {
            "_id": 0,
            keys.BARCODES: 1,
            keys.PROMOTED: 1,
            keys.VARIANTS: 1,
            keys.VARIANT_NAME: 1,
            keys.LINK: 1,
        },
    )
    mongosync = MongoSync(collections.items_backup_collection, write_interval=300)

    BACKUP_KEYS = {keys.BARCODES, keys.PROMOTED, keys.VARIANTS, keys.VARIANT_NAME}
    docs_to_backup = []
    for doc in tqdm(item_cursor):
        if any([key in doc for key in BACKUP_KEYS]):
            docs_to_backup.append(doc)
            if len(docs_to_backup) > 300:
                mongosync.batch_update_mongo(docs_to_backup)
                docs_to_backup = []

    mongosync.batch_update_mongo(docs_to_backup)
    print("items_collection backed up!")
