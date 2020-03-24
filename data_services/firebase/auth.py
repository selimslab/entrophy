import os

from services import json_util

dir_name = os.path.dirname(__file__)
json_name = "cred.json"
cred_path = os.path.join(dir_name, json_name)

cred = {
    "type": "service_account",
    "project_id": "narmoni-e8761",
    "private_key_id": "d4f4617415bc39190db51eb31a3b06873564946b",
    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEugIBADANBgkqhkiG9w0BAQEFAASCBKQwggSgAgEAAoIBAQCdSnTrm4I1fx8p\ns5Lib/Xu0b1FRugziSyuFHl0rJwRdT27sq2Tkp+XmRhqE6LKbNpbzOk52tnUr6Jg\n/9FKPi8FFNJp7MGqM7kExxHVh9CYhwJNXriM2FLifxg0+qy4ygbNdKcMvrZpIIL9\nP8NOT6fbABGG2gVizHxM0tHq1ZWz8FmlB7WCN2z8mgSG8AK/anM6171jUDbQT4hS\nVpH9OTP0X0VfbRRu0FiqNQOlkauFyJI76puuSlnWPi4KQcV5P8V03NmM85bqzx6T\n32aVbWfvyYQyZziCSumG6S13WxICX+51qGR1JTKnUwuHaalH2M1aJentrP6OTm9I\nRQ0HFfLXAgMBAAECgf8oiQJI6swYQbozaRb+o9tTpqb1UFdKj9Pc0RUEuYA2l8wm\niSE4LBN/d9FFOKyY2YHFgxI0qfpMzdYP292L7sZtekV5hNsF/RsSmUkngRmCKf0k\nEGAr92Ub5VSypdCnzrJSdF/Vo7uxXtjnXV1ysN5hHW6pl++wmZlM0HKGS9OCmWk+\nB38jCuw1vxRXze6qxosloeCbzsryKGXRE6INa4a2zw7zriE4J8Jq8uPEQnAb46qV\nvauSMV9q52PD350ktU6xAD66uuuv7FeEACNbSXXf7RzT88HVkR1Dqcn9rebwO7UO\nCrc/AEFfKpAKujxFLEkVt875Z236nwwnGLVyk1kCgYEAzjAMIDNGavu6qK2TSn4U\neeV182NGN3j1D+GhOFnrHpZyngDk68DuCThWg9cRb9YgmJdVoWsDrydtVucLz/n+\nWfI98yA9ARCtIEtqo/oHNfbkdMbpbSE070XNb/zYipj23K4b9WEIo2BUGKS62Bwl\n7F67KPEtbFEU+3cn2iQfSskCgYEAw0pRsMSC6O3X4Skd5TE09wLZs+ReyHBVxVqz\nhMeHpmRdAr7u4bLJ1gv7vlfVBrXxnz9Ognc14sg4y9Apxs68XPCyAPO6yDkt5bjP\nSkAE5BkDFrwBKko8gB5U4ufMrISNi1GUyC0GETz1tKVAqjieo5c+/4Nsacx9ZKU8\nph8ygJ8CgYBOqAOoMQdW/qrpeDXtQAW9rqx9acy6krkiEtf28E6Cf7A/2GV8DkCA\nYe6XIu9y84PB0lGHX5SrN+Y9NazK7Tp7w66gVhcPlfYFkN+gqFwh2Qq0BcG8sONJ\nuB4z74gH72yVKRJfXGH4OWI7eHQSx0IsVsMdTkweuxu/Bmi8jfUmCQKBgG4H6KD9\nB3kv0OtG3FYu9FWcIIbvy8uJJ3pLkUvlk/NXJuSOKU+3CWt1UwC6wgbG6n08EQMH\nIbBF+WI0ReWCw7Rl1RUePgXj2Y1OJFUEXv0ZbpkXklx+eToCXPd/fN1SzeFKNNbY\nL0v1GccPOLDvt8oaRF94b9PoaFoVk2dRuoWnAoGAYu7S5LPdWrSBU6RUl+HuUL7u\nkjVcPaWWQLMr+zdCGFzE0qeP3+0M5zmTnMYrkUoTRaNpP/L2pTIllMrI/mag8Q7x\nZCne2R5QpEoWe+nboOSC7vQB5F2/8dpDUaiRHYQxX/ivkoJNJ7tKZb2h6HUV0JKl\noFRZ1YY1g3Nfe3nEIr8=\n-----END PRIVATE KEY-----\n",
    "client_email": "firebase-adminsdk-t92qz@narmoni-e8761.iam.gserviceaccount.com",
    "client_id": "112280029961644900238",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-t92qz%40narmoni-e8761.iam.gserviceaccount.com",
}
if not os.path.exists(cred_path):
    json_util.save_json(cred_path, cred)
