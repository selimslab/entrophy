from pymongo import UpdateOne, InsertOne, UpdateMany, ReplaceOne
from pymongo.errors import BulkWriteError
from tqdm import tqdm

import constants as keys


class MongoSync:
    def __init__(self, collection, write_interval=None):
        if write_interval is None:
            self.write_interval = 4096
        else:
            self.write_interval = write_interval

        self.ops = list()
        self.collection = collection

    def bulk_exec(self, debug=False):
        if self.ops:
            try:
                self.collection.bulk_write(self.ops, ordered=False)
                if debug:
                    print("bulk write successful!", "written", len(self.ops), "items")
                self.ops = list()
            except BulkWriteError as bwe:
                print(bwe.details)
                # clear ops to prevent cascading failure
                self.ops = list()
                raise

    def add_update(self, selector, command):
        new_op = UpdateOne(selector, command, upsert=True)
        self.ops.append(new_op)

        if len(self.ops) >= self.write_interval:
            self.bulk_exec()

    def add_multiple_update(self, selector, command):
        new_op = UpdateMany(selector, command, upsert=True)
        self.ops.append(new_op)
        self.bulk_exec()

    def batch_insert(self, docs):
        if not docs:
            return
        for doc in tqdm(docs):
            self.ops.append(InsertOne(doc))

        if len(self.ops) >= self.write_interval:
            self.bulk_exec()

    def add_replace(self, filter, replacement):
        self.ops.append(ReplaceOne(filter=filter, replacement=replacement))
        if len(self.ops) >= self.write_interval:
            self.bulk_exec()

    def batch_update_mongo(self, docs):
        if not docs:
            return
        print("updating", len(docs), "mongo docs..")
        for doc in tqdm(docs):
            if not doc:
                continue
            link = doc.get(keys.LINK)
            if not link:
                continue
            selector = {keys.LINK: link}
            command = {"$set": doc}
            self.add_update(selector, command)

        self.bulk_exec()
