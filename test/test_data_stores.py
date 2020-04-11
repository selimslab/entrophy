from data_services .firebase.connect import test_collection

# print(test_collection.document("test").get().to_dict())


def test_firestore():
    docs = test_collection.stream()
    for doc in docs:
        print(u'{} => {}'.format(doc.id, doc.to_dict()))