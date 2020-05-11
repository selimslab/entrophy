import services

fullskus = services.read_json("all_docs/full_skus.json")

names = [sku.get("names") for sku in fullskus.values()]

services.save_json("name_groups.json", names)
