from pymongo import MongoClient

CONNECTION_STRING = "mongodb+srv://selim:selimslab@market-8lznc.mongodb.net/test?retryWrites=true&w=majority"
client = MongoClient(CONNECTION_STRING)
db = client.narmoni

NEWDB = "mongodb+srv://selim:e6nanmCqhMwOQq8q@cluster1-gx1ov.mongodb.net/test?retryWrites=true&w=majority"
newclient = MongoClient(NEWDB)

newdb = newclient.main

