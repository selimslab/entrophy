import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from firebase_admin.exceptions import (
    NotFoundError,
    InvalidArgumentError,
    AbortedError,
    FirebaseError,
)
from tqdm import tqdm
import logging
from .auth import cred_path

# Use a service account
cred = credentials.Certificate(cred_path)

firebase_admin.initialize_app(cred)

firestore_client = firestore.client()
skus_collection = firestore_client.collection(u"skus")
batch_size = 300


def commit_batch(batch):
    try:
        batch.commit()
    except (NotFoundError, AbortedError, FirebaseError, InvalidArgumentError) as e:
        logging.error(e)
    finally:
        batch = firestore_client.batch()
        return batch


def batch_update_firestore(docs, create=None):
    if create is None:
        create = True

    batch = firestore_client.batch()
    count = 0

    for doc in docs:
        object_id = doc.get("objectID")
        doc_ref = skus_collection.document(object_id)
        if create:
            batch.set(doc_ref, doc)
        else:
            batch.update(doc_ref, doc)

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


def delete_collection(batch_size):
    docs = skus_collection.limit(batch_size).stream()
    deleted = 0

    for doc in docs:
        print(u"Deleting doc {} => {}".format(doc.id, doc.to_dict()))
        doc.reference.delete()
        deleted = deleted + 1

    if deleted >= batch_size:
        return delete_collection(batch_size)


def firestore_all_skus_generator():
    skus_ref = firestore_client.collection(u"skus")

    query = skus_ref.order_by("objectID").limit(300)
    docs = query.stream()

    while docs:

        sku_id = None
        for doc in docs:
            sku = doc.to_dict()
            sku_id = sku.get(u"objectID")
            yield sku

        if sku_id:
            next_query = (
                skus_ref.order_by(u"objectID")
                .start_after({u"objectID": sku_id})
                .limit(300)
            )

            docs = next_query.stream()

        else:
            docs = []


def firestore_generate_skus_by_id(ids):
    if ids is None:
        ids = list()

    skus_ref = firestore_client.collection(u"skus")
    batch, rest = ids[:10], ids[10:]
    query = skus_ref.where(u"objectID", u"in", batch)
    docs = query.stream()

    for doc in docs:
        yield doc.to_dict()
        # sku_id = sku.get(u"objectID")

    if rest:
        firestore_generate_skus_by_id(rest)


if __name__ == "__main__":
    pass
