import services
from pprint import pprint
from collections import defaultdict

ty = services.read_json("ty_filters2.json")

merged = defaultdict(set)  # uses set to avoid duplicates

for cat, filters in ty.items():
    for k, v in filters.items():  # use d.iteritems() in python 2
        merged[k].update(v)

pprint(merged)

brand = merged.get("brand")
pprint(brand)
print(len(brand))
