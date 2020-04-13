import constants as keys
import data_services
from data_services.firebase.connect import skus_collection


def instant_price_update(existing_link_id_pairs, instant_update_batch):
    existing_ids = list(existing_link_id_pairs.values())
    if not existing_ids:
        return

    body = {
        "_source": {"includes": ["prices"]},
        "query": {"ids": {"values": existing_ids}},
    }

    existing_elastic_docs = data_services.elastic.scroll(body=body)

    id_price_pairs = {
        doc.get("_id"): doc.get("_source", {}).get("prices", {})
        for doc in existing_elastic_docs
    }

    instant_updates = []

    for link, item in instant_update_batch:
        sku_id = existing_link_id_pairs.get(link)
        old_prices = id_price_pairs.get(sku_id)
        if old_prices:
            price_update = {item.get(keys.MARKET): item.get(keys.PRICE)}
            new_prices = {**old_prices, **price_update}
            # TODO LAST_UPDATED, but will you show a time besides every price?
            update = {keys.SKU_ID: sku_id, keys.PRICES: new_prices}
            instant_updates.append(update)

    data_services.elastic.update_docs(instant_updates, index="products")
    data_services.batch_update_firestore(instant_updates, collection=skus_collection)
