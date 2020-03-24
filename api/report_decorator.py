import traceback

from elasticsearch.exceptions import ElasticsearchException
from firebase_admin.exceptions import FirebaseError
from pymongo.errors import PyMongoError

from services.ses import send_email
import logging

from functools import wraps


def handle_error(err, traceback):
    try:
        report = "\n\n".join([str(err), str(traceback.format_exc())])
        send_email("supermatch error", report)
    except (TypeError, AttributeError, KeyError, ValueError) as e:
        logging.error(e)


def report_decorator(func):
    @wraps(func)
    def wrap_func(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except (
            FirebaseError,
            ElasticsearchException,
            PyMongoError,
            KeyError,
            ValueError,
            TypeError,
            IndexError,
            AttributeError,
        ) as err:
            logging.error(err)
            logging.error(traceback.format_exc())
            handle_error(err, traceback)

    return wrap_func
