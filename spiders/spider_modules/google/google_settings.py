GOOGLE_SETTINGS = {
    "ITEM_PIPELINES": {"spiders.pipelines.search_pipeline.SearchPipeline": 300},
    "DOWNLOAD_TIMEOUT": 12,
    "RETRY_ENABLED": False,
    "DOWNLOAD_DELAY": 2,
    "USER_AGENT": "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1)",
    "CLOSESPIDER_TIMEOUT": 48000,
}
