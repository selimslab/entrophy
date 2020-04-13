from data_services.firebase.connect import test_collection


def test_firestore():
    # print(test_collection.document("test").get().to_dict())
    docs = test_collection.stream()
    for doc in docs:
        print(u"{} => {}".format(doc.id, doc.to_dict()))
