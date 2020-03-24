import json


def read_json(path):
    print("reading", path)
    with open(path, "r") as f:
        data = json.load(f)
        print(len(data))
        return data


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as outfile:
        json.dump(data, outfile, ensure_ascii=False, indent=4)
        print("written to", path, len(data))
