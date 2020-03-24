import elasticsearch.exceptions as elastic_errors
import firebase_admin.exceptions as fire_errors

import constants as keys
import data_services


class InstantUpdater:
    def __init__(self):
        self.elastic_update_batch = []
        self.firestore_update_batch = []
        self.batch_size = 256

        self.link_doc_pairs = {}
        self.id_sku_pairs = {}
        self.id_product_pairs = {}

    def get_snapshot(self):
        if not self.link_doc_pairs:
            self.link_doc_pairs = data_services.get_link_doc_pairs()
        if not self.id_product_pairs:
            self.id_product_pairs = data_services.get_id_product_pairs()
        if not self.id_sku_pairs:
            self.id_sku_pairs = data_services.get_id_sku_pairs(self.id_product_pairs)

    def produce_event(self, price_update, existing_doc):
        product_id = existing_doc.get(keys.PRODUCT_ID)
        old_product = self.id_product_pairs.get(product_id, {})
        old_prices = old_product.get(keys.PRICES)
        update = dict()

        if old_product and keys.PRICES in old_product:
            update[keys.PRICES] = {**old_prices, **price_update}
            if product_id:
                update[keys.objectID] = str(product_id)
            self.elastic_update_batch.append(update)

        sku_id = existing_doc.get(keys.SKU_ID)
        old_sku = self.id_sku_pairs.get(sku_id, {})
        old_prices = old_sku.get(keys.PRICES)

        if old_sku and keys.PRICES in old_sku:
            old_sku[keys.PRICES] = {**old_prices, **price_update}
            if sku_id:
                old_sku[keys.objectID] = str(sku_id)
            self.firestore_update_batch.append(old_sku)

        self.check_batches()

    def check_batches(self):
        if len(self.firestore_update_batch) >= self.batch_size:
            self.instant_update_firestore()

        if len(self.elastic_update_batch) >= self.batch_size:
            self.instant_update_elastic()

    def instant_update_elastic(self):
        try:
            data_services.update_elastic_docs(self.elastic_update_batch)
        except (
            elastic_errors.ElasticsearchException,
            elastic_errors.NotFoundError,
            elastic_errors.ConnectionTimeout,
        ) as e:
            print(e)
            # send_email("ElasticsearchException", str(e))
        finally:
            self.elastic_update_batch = []

    def instant_update_firestore(self):
        try:
            data_services.batch_update_firestore(self.firestore_update_batch)
        except (
            fire_errors.FirebaseError,
            fire_errors.NotFoundError,
            fire_errors.InternalError,
        ) as e:
            print(e)
            # send_email("FirebaseError", str(e))
        finally:
            self.firestore_update_batch = []


instant_updater = InstantUpdater()
