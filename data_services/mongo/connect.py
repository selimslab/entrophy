from pymongo import MongoClient

"""
from dotenv import load_dotenv
import os
load_dotenv()
CONNECTION_STRING = os.environ.get("CONNECTION_STRING")
"""

CONNECTION_STRING = "mongodb+srv://selim:selimslab@market-8lznc.mongodb.net/test?retryWrites=true&w=majority"
client = MongoClient(CONNECTION_STRING)
db = client.narmoni


backup_client = MongoClient(
    "mongodb+srv://selim:3924boun@cluster0-ztyl6.mongodb.net/test?retryWrites=true&w=majority"
)
backup_db = backup_client.backups
