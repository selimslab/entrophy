import constants as keys


class ItemContentMonitor:
    def __init__(self):
        self.bad_content = list()
        self.keys = {keys.LINK, keys.NAME, keys.PRICE, keys.MARKET, keys.SRC}

    def check_for_content_anomalies(self, item):
        if any(key not in item for key in self.keys):
            self.bad_content.append(item)
