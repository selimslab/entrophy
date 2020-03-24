from .connect import db

items_collection = db["items"]

## TODO change to backup_db
items_backup_collection = db["items_backup_collection"]

skus_collection = db["skus"]
products_collection = db["products"]

subs_collection = db["subs"]

test_collection = db["test"]
