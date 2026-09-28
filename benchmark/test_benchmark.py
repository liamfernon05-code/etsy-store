"""Offline test of the benchmark logic with a fake Etsy API. Run: python -m benchmark.test_benchmark"""

import time

from benchmark import etsy_benchmark as eb

NOW = time.time()


def fake_get(path, params=None):
    if path == "/listings/active":
        n = 5
        return {"count": 1800, "results": [
            {"listing_id": i, "shop_id": i % 3, "title": f"golden retriever sweatshirt {i}", "url": f"u{i}",
             "price": {"amount": 3999 + i * 100, "divisor": 100}, "num_favorers": 50 * (i + 1), "views": 900} for i in range(n)]}
    sid = int(path.rsplit("/", 1)[1])
    return {"create_date": NOW - (100 * 86400 if sid == 0 else 800 * 86400), "transaction_sold_count": 250 if sid == 0 else 5000,
            "review_count": 40, "review_average": 4.9}


eb.http_get = fake_get
k = eb.analyse_keyword("golden retriever sweatshirt", 50, {}, now=NOW)
assert k["total_results"] == 1800 and k["sampled"] == 5
assert k["new_shops_with_100_sales"] == 1, k  # shop 0 only, even though 2 of its listings are on page one
assert k["top_by_favorers"][0]["favorers"] == 250
assert k["price_median"] == 41.99, k["price_median"]
v = eb.verdict("01", [k], 44.99)
assert v["sell_likelihood_heuristic"] in ("Higher", "Medium", "Lower")
print("ok:", v)
