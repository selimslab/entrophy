import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from .save_creds import cred_path

# Use a service account
cred = credentials.Certificate(cred_path)
firebase_admin.initialize_app(cred)

firestore_client = firestore.client()
skus_collection = firestore_client.collection(u"skus")
config_collection = firestore_client.collection(u"config")
test_collection = firestore_client.collection(u"test")
batch_size = 300
