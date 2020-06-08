import services
import constants as keys
from paths import input_dir, output_dir


def inspect_results(docs):
    with_brand_only = [
        doc for doc in docs if keys.BRAND in doc and keys.SUBCAT not in doc
    ]
    services.save_json(output_dir / "with_brand_only.json", with_brand_only)

    with_subcat_only = [
        doc for doc in docs if keys.BRAND not in doc and keys.SUBCAT in doc
    ]
    services.save_json(output_dir / "with_subcat_only.json", with_subcat_only)

    with_brand_and_sub = [
        doc for doc in docs if keys.BRAND in doc and keys.SUBCAT in doc
    ]
    services.save_json(output_dir / "with_brand_and_sub.json", with_brand_and_sub)

    brands_in_results = [doc.get(keys.BRAND) for doc in docs]
    subcats_in_results = [doc.get(keys.SUBCAT) for doc in docs]

    services.save_json(
        output_dir / "brands_in_results.json",
        sorted(services.dedup_denull(brands_in_results)),
    )
    services.save_json(
        output_dir / "subcats_in_results.json",
        sorted(services.dedup_denull(subcats_in_results)),
    )

    with_brand = services.count_fields(docs, keys.BRAND)
    with_sub = services.count_fields(docs, keys.SUBCAT)

    print(
        "total",
        len(docs),
        "\n",
        "with_brand",
        with_brand,
        "\n",
        "with_sub",
        with_sub,
        "\n",
        "with_subcat_only",
        len(with_subcat_only),
        "\n",
        "with_brand_only",
        len(with_brand_only),
        "\n",
        "with_both_brand_and_subcat",
        len(with_brand_and_sub),
        "\n",
    )
