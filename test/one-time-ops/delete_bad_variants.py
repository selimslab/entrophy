from data_services.mongo.collections import items_collection
from bson import ObjectId
from pprint import pprint
import services
import constants as keys


def check_lang():
    q = {keys.VARIANTS: {"$exists": True}, keys.MARKET: keys.GOOGLE}
    cursor = items_collection.find(q, {keys.VARIANTS: 1})
    services.json_util.save_json("vars.json", list(cursor))

    russian = {
        "б",
        "в",
        "г",
        "д",
        "ж",
        "з",
        "к",
        "л",
        "м",
        "н",
        "п",
        "р",
        "с",
        "т",
        "ф",
        "х",
        "ц",
        "ч",
        "ш",
        "щ",
        "а",
        "э",
        "ы",
        "у",
        "о",
        "я",
        "е",
        "ё",
        "ю",
        "и",
        "ß",
        "ä",
    }
    # search_fs_by_object_ids(x)
    # vars = services.json_util.read_json("varnew.json")

    q = {keys.VARIANTS: {"$exists": True}, keys.MARKET: keys.GOOGLE}
    cursor = items_collection.find(q, {keys.VARIANTS: 1})

    to_delete = set()
    for doc in cursor:
        keys = doc.get("variants", {}).keys()
        r = [r in key for r in russian for key in keys]
        if any(r):
            to_delete.add(str(doc.get("_id")))
            pprint(keys)

    services.json_util.save_json("bad.json", list(to_delete))

    bad = services.json_util.read_json("bad.json")
    bad = [ObjectId(b) for b in bad]
    items_collection.delete_many({"_id": {"$in": bad}})
