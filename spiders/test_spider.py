from scrapy.crawler import CrawlerProcess


def debug_spider(spider_class, test_generator=None):
    process = CrawlerProcess(
        {"USER_AGENT": "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1"}
    )
    if test_generator is not None:
        process.crawl(spider_class, generator=test_generator)
    else:
        process.crawl(spider_class, debug=True)

    process.start()
