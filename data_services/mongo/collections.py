from .connect import db

items_collection = db["raw_products"]

items_backup = db["raw_products_backup"]

test_collection = db["test"]

elastic_backup = db["elastic_backup"]
