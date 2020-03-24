from services.ses import send_email


def email_stats(crawlers):
    relevant_keys = {
        "downloader/request_count": "req",
        "downloader/response_count": "res",
        "downloader/response_status_count/200": "200",
        "log_count/ERROR": "error",
        "item_scraped_count": "items",
        "elapsed_time_seconds": "time",
    }

    all_stats = []
    for name, crawler in crawlers.items():
        stats = crawler.stats.get_stats()
        stats = {
            relevant_keys[k]: v for k, v in stats.items() if k in relevant_keys.keys()
        }
        if "error" not in stats:
            continue
        if stats.get("error") < stats.get("req"):
            continue
        if "time" in stats:
            stats["time"] = stats.pop("time") // 60
        stats["name"] = name
        all_stats.append(name)
        all_stats.append(stats)

    if all_stats:
        all_stats = [str(d) for d in all_stats]
        subject = "refresh report"
        body_text = "\n\n".join(all_stats)
        send_email(subject, body_text)
