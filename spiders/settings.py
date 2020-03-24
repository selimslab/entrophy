# -*- coding: utf-8 -*-

# Scrapy settings for src project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://doc.scrapy.org/en/latest/topics/settings.html
#     https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://doc.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = "proton"

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

SPIDER_MODULES = [
    "spiders.spider_modules.visible.barcodeless",
    "spiders.spider_modules.visible.with_search",
    "spiders.spider_modules.visible.barcode_sources",
    "spiders.spider_modules.helper_markets",
    "spiders.spider_modules.google",
]
NEWSPIDER_MODULE = "spiders"

# Configure item pipelines
# See https://doc.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {"spiders.pipelines.market_pipeline.MarketPipeline": 300}

FEED_EXPORT_ENCODING = "utf-8"

DOWNLOAD_DELAY = 2

AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 2
AUTOTHROTTLE_MAX_DELAY = 12

DOWNLOAD_TIMEOUT = 20

RETRY_ENABLED = True

RETRY_TIMES = 1
RETRY_HTTP_CODES = [500, 502, 503, 504, 400, 403, 404, 408]

LOG_LEVEL = "DEBUG"
LOG_FORMAT = "%(levelname)s: %(message)s"

SPIDERMON_ENABLED = False

EXTENSIONS = {
    # 'spidermon.contrib.scrapy.extensions.Spidermon': 500,
}

# Disable cookies (enabled by default)
COOKIES_ENABLED = False


# Configure maximum concurrent requests performed by Scrapy (default: 16)

# Configure a delay for requests for the same website (default: 0)
# See https://doc.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
# The download delay setting will honor only one of:
# CONCURRENT_REQUESTS_PER_DOMAIN = 16
# CONCURRENT_REQUESTS_PER_IP = 16

# Disable Telnet Console (enabled by default)
# TELNETCONSOLE_ENABLED = False

# Override the default request headers:
DEFAULT_REQUEST_HEADERS = {
    "Accept": "text/html,application/json",
    "Accept-Language": "tr, en",
    "Connection": "keep-alive",
}

# Enable or disable spider middlewares
# See https://doc.scrapy.org/en/latest/topics/spider-middleware.html
# SPIDER_MIDDLEWARES = {
#    'middlewares.MarketSpiderMiddleware': 543,
# }

# Enable or disable downloader middlewares
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
# DOWNLOADER_MIDDLEWARES = {
#    'middlewares.MarketDownloaderMiddleware': 543,
# }

# Enable or disable extensions
# See https://doc.scrapy.org/en/latest/topics/extensions.html
# EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
# }


# Enable and configure the AutoThrottle extension (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/autothrottle.html
# The initial download delay

# The average number of requests Scrapy should be sending in parallel to
# each remote server
# AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
# AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
# HTTPCACHE_ENABLED = True
# HTTPCACHE_EXPIRATION_SECS = 0
# HTTPCACHE_DIR = 'httpcache'
# HTTPCACHE_IGNORE_HTTP_CODES = []
# HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'
