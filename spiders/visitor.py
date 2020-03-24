from pymongo.errors import (
    ConnectionFailure,
    DuplicateKeyError,
    DocumentTooLarge,
    InvalidDocument,
    OperationFailure,
    BulkWriteError,
)
import logging
from requests.exceptions import SSLError
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from services import send_email


def run_spiders_simultaneously(spiders: dict):
    default_settings = get_project_settings()
    default_settings["LOG_LEVEL"] = "ERROR"

    process = CrawlerProcess(default_settings)
    errors = list()
    try:
        crawlers = dict()
        for name, spider_class in spiders.items():
            logging.info(f"running {name}")
            crawler = process.create_crawler(spider_class)
            crawlers[name] = crawler
            try:
                process.crawl(crawler)
            except (AttributeError, TypeError, KeyError, ValueError, ImportError) as e:
                logging.error(e)
                continue

        process.start()
        # email_stats(crawlers)
    except (AttributeError, TypeError, KeyError, ValueError, ImportError) as e:
        logging.error(e)
        errors.append(e)
    except (
        SSLError,
        ConnectionError,
        ConnectionAbortedError,
        ConnectionRefusedError,
        TimeoutError,
    ) as network_error:
        logging.error(network_error)
        errors.append(network_error)
    except (
        ConnectionFailure,
        DuplicateKeyError,
        DocumentTooLarge,
        InvalidDocument,
        OperationFailure,
        BulkWriteError,
    ) as pymongo_error:
        logging.error(pymongo_error)
        errors.append(pymongo_error)

    if errors:
        subject = str(len(errors)) + " spider errors"
        body_text = "\n\n".join(errors)
        send_email(subject, body_text)
