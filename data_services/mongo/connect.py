from pymongo import MongoClient

client = MongoClient(
    "mongodb+srv://selim:e6nanmCqhMwOQq8q@cluster1-gx1ov.mongodb.net/test?retryWrites=true&w=majority"
)
db = client.Cluster1
