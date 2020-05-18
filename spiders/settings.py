BOT_NAME = "nm"

SPIDER_MODULES = [
    "spiders.spider_modules.visible.barcodeless",
    "spiders.spider_modules.visible.with_search",
    "spiders.spider_modules.visible.barcode_sources",
    "spiders.spider_modules.visible.ty",
    "spiders.spider_modules.helper_markets",
    "spiders.spider_modules.google",
]
NEWSPIDER_MODULE = "spiders"

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

COOKIES_ENABLED = False
ROBOTSTXT_OBEY = False

CLOSESPIDER_ERRORCOUNT = 200
CLOSESPIDER_TIMEOUT = 7200

# Override the default request headers:
DEFAULT_REQUEST_HEADERS = {
    "Accept": "text/html,application/json",
    "Accept-Language": "tr, en",
    "Connection": "keep-alive",
}
