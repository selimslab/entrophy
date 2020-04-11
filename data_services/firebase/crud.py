from data_services.firebase.connect import *
import constants as keys
from tqdm import tqdm


def commit_batch(batch):
    try:
        batch.commit()
    finally:
        return firestore_client.batch()


def batch_process(docs, collection, batch, func):
    count = 0

    for doc in docs:
        doc_id = doc.get(keys.SKU_ID)
        doc_ref = collection.document(doc_id)
        func(doc_ref, doc)
        # batch.set(doc_ref, doc)
        count += 1
        if count == batch_size:
            batch = commit_batch(batch)
            count = 0

    commit_batch(batch)


def batch_update(docs, collection):
    batch = firestore_client.batch()
    batch_process(docs, collection, batch, batch.update)


def batch_replace(docs, collection):
    batch = firestore_client.batch()
    batch_process(docs, collection, batch, batch.set)


def delete_all():
    docs = skus_collection.limit(batch_size).get()
    deleted = 0
    for doc in tqdm(docs):
        if doc.id.isdigit():
            print(u"Deleting", doc.id)
            doc.reference.delete()
            deleted = deleted + 1

    if deleted >= batch_size:
        return delete_all()


def delete_by_ids(ids_to_delete, collection):
    print("deleting", len(ids_to_delete), "docs from firestore")
    batch = firestore_client.batch()
    count = 0
    for object_id in tqdm(ids_to_delete):
        doc_ref = collection.document(object_id)
        batch.delete(doc_ref)
        count += 1
        if count >= batch_size:
            batch.commit()
            count = 0
            batch = firestore_client.batch()

    batch.commit()


def sync_firestore(updates):
    collection = test_collection

    to_be_added, to_be_updated, ids_to_delete = updates
    print(f"adding {len(to_be_added)} docs")
    batch_replace(to_be_added, collection)

    print(f"updating {len(to_be_updated)} docs")
    batch_replace(to_be_updated, collection)

    print(f"deleting {len(ids_to_delete)} docs")
    if ids_to_delete:
        delete_by_ids(ids_to_delete, collection)


def search_in_firestore(doc_id):
    # fs.batch_update_firestore([test])
    doc_ref = firestore_client.collection("skus").document(doc_id)
    doc = doc_ref.get()
    print(doc.to_dict())


if __name__ == "__main__":
    doc_ref = firestore_client.collection(u"config").document(u"search")
    doc = doc_ref.get()
    print(doc.to_dict())
