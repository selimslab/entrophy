from .main import firestore_client, skus_collection, batch_size
import constants as keys
from tqdm import tqdm


def commit_batch(batch):
    try:
        batch.commit()
    finally:
        batch = firestore_client.batch()
        return batch


def batch_update_firestore(docs):
    batch = firestore_client.batch()
    count = 0

    for doc in docs:
        doc_id = doc.get(keys.SKU_ID)
        doc_ref = skus_collection.document(doc_id)
        batch.update(doc_ref, doc)
        # batch.set(doc_ref, doc)
        count += 1
        if count == batch_size:
            batch = commit_batch(batch)
            count = 0

    commit_batch(batch)


def delete_old_docs():
    docs = skus_collection.limit(batch_size).get()
    deleted = 0
    for doc in tqdm(docs):
        if doc.id.isdigit():
            print(u"Deleting", doc.id)
            doc.reference.delete()
            deleted = deleted + 1

    if deleted >= batch_size:
        return delete_old_docs()


def delete_old_ids(ids_to_delete):
    print("deleting", len(ids_to_delete), "docs from firestore")
    batch = firestore_client.batch()
    count = 0
    for object_id in tqdm(ids_to_delete):
        doc_ref = skus_collection.document(object_id)
        batch.delete(doc_ref)
        count += 1
        if count >= batch_size:
            batch.commit()
            count = 0
            batch = firestore_client.batch()

    batch.commit()


def sync_firestore(updates):
    print("syncing skus..")
    to_be_added, to_be_updated, ids_to_delete = updates
    batch_update_firestore(to_be_added)
    batch_update_firestore(to_be_updated)
    if ids_to_delete:
        delete_old_ids(ids_to_delete)


def search_in_firestore(doc_id):
    # fs.batch_update_firestore([test])
    doc_ref = firestore_client.collection("skus").document(doc_id)
    doc = doc_ref.get()
    print(doc.to_dict())
