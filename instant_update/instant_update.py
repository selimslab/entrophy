import constants as keys
import data_services


class InstantUpdater:
    def __init__(self):
        self.batch = []
        self.batch_size = 256

        self.link_doc_pairs = {}
        self.old_docs = {}

    def get_snapshot(self):
        if not self.link_doc_pairs:
            self.link_doc_pairs = data_services.get_link_doc_pairs()
        if not self.old_docs:
            self.old_docs = data_services.get_id_product_pairs()

    def produce_event(self, price_update, existing_doc):
        sku_id = existing_doc.get(keys.SKU_ID)
        old_doc = self.old_docs.get(sku_id, {})
        old_prices = old_doc.get(keys.PRICES)
        update = dict()

        if old_doc and keys.PRICES in old_doc:
            update[keys.PRICES] = {**old_prices, **price_update}
            if sku_id:
                update[keys.SKU_ID] = str(sku_id)
            self.batch.append(update)

        if len(self.batch) >= self.batch_size:
            self.instant_update_elastic()

    def instant_update_elastic(self):
        try:
            data_services.update_elastic_docs(self.batch)
        finally:
            self.batch = []


instant_updater = InstantUpdater()
