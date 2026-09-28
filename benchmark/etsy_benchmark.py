"""Benchmark our designs against live Etsy listings using the official Etsy Open API v3.

Uses only the sanctioned API (no HTML scraping, which Etsy's terms prohibit). Needs your own free API key:
  1. Create an app at https://www.etsy.com/developers/register (personal, non-commercial access is enough to read listings).
  2. export ETSY_API_KEY=<keystring>            (and ETSY_API_SECRET=<shared secret> if your app requires "keystring:secret")
  3. The environment must be allowed to reach openapi.etsy.com.
Run:  python -m benchmark.etsy_benchmark [--per-keyword 50] [--only 01-retriever-in-name-only]
Output: benchmark/results.json and benchmark/REPORT.md

What Etsy exposes: result counts, price, favourites, views, tags, shop age, shop total sales, shop rating.
What it does NOT expose: sales per listing. Shop-level sales and reviews are the public proxies, so the verdicts
below are heuristics that rank risk, not sales forecasts.
"""

import argparse
import json
import os
import statistics
import time
import urllib.parse
import urllib.request
from pathlib import Path

BASE = "https://openapi.etsy.com/v3/application"
HERE = Path(__file__).parent
YEAR = 365 * 24 * 3600


def http_get(path, params=None):
    key = os.environ["ETSY_API_KEY"]
    if os.environ.get("ETSY_API_SECRET"):
        key = f"{key}:{os.environ['ETSY_API_SECRET']}"
    url = f"{BASE}{path}" + ("?" + urllib.parse.urlencode(params) if params else "")
    req = urllib.request.Request(url, headers={"x-api-key": key, "Accept": "application/json"})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                time.sleep(0.15)  # stay well under Etsy's rate limits
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503) and attempt < 3:
                time.sleep(2 ** attempt)
                continue
            raise


def price_of(listing):
    p = listing.get("price") or {}
    return p.get("amount", 0) / (p.get("divisor") or 100)


def get_shop(shop_id, cache):
    if shop_id not in cache:
        try:
            cache[shop_id] = http_get(f"/shops/{shop_id}")
        except Exception as e:  # tolerate closed shops etc.
            cache[shop_id] = {"_error": str(e)}
    return cache[shop_id]


def analyse_keyword(kw, per_keyword, shop_cache, now=None):
    now = now or time.time()
    data = http_get("/listings/active", {"keywords": kw, "limit": min(per_keyword, 100), "sort_on": "score", "sort_order": "desc"})
    results = data.get("results", [])
    rows = []
    for l in results:
        shop = get_shop(l.get("shop_id"), shop_cache)
        created = shop.get("create_date") or 0
        rows.append({
            "shop_id": l.get("shop_id"), "title": l.get("title", ""), "url": l.get("url", ""), "price": round(price_of(l), 2),
            "favorers": l.get("num_favorers", 0), "views": l.get("views", 0),
            "shop_sales": shop.get("transaction_sold_count"), "shop_reviews": shop.get("review_count"),
            "shop_rating": shop.get("review_average"), "shop_age_days": int((now - created) / 86400) if created else None,
        })
    prices = [r["price"] for r in rows if r["price"]]
    ages = [r["shop_age_days"] for r in rows if r["shop_age_days"] is not None]
    new_shops = [r for r in rows if r["shop_age_days"] is not None and r["shop_age_days"] < 365]
    new_winners = {r["shop_id"] for r in new_shops if (r["shop_sales"] or 0) >= 100}  # distinct shops, not listings
    return {
        "keyword": kw, "total_results": data.get("count"), "sampled": len(rows),
        "price_median": round(statistics.median(prices), 2) if prices else None,
        "price_p25": round(statistics.quantiles(prices, n=4)[0], 2) if len(prices) >= 4 else None,
        "price_p75": round(statistics.quantiles(prices, n=4)[2], 2) if len(prices) >= 4 else None,
        "median_favorers": statistics.median([r["favorers"] for r in rows]) if rows else None,
        "new_shop_share": round(len(new_shops) / len(ages), 2) if ages else None,
        "new_shops_with_100_sales": len(new_winners), "new_winner_shop_ids": sorted(new_winners),
        "top_by_favorers": sorted(rows, key=lambda r: r["favorers"], reverse=True)[:5],
        "rows": rows,
    }


def verdict(design, kws, our_price):
    """Heuristics taken from the niche debate's kill tests. They rank risk; they do not forecast sales."""
    totals = [k["total_results"] for k in kws if k["total_results"] is not None]
    slogan = kws[0]
    reasons, score = [], 0
    if totals:
        best = min(totals)
        if best < 3000: score += 2; reasons.append(f"a target keyword has only {best:,} results (winnable)")
        elif best < 20000: score += 1; reasons.append(f"lowest keyword competition is {best:,} results (moderate)")
        else: reasons.append(f"every keyword has {best:,}+ results (crowded)")
    nw = len({sid for k in kws for sid in k["new_winner_shop_ids"]})
    if nw >= 3: score += 2; reasons.append(f"{nw} shops under 12 months old already have 100+ sales (a new shop can break in)")
    elif nw >= 1: score += 1; reasons.append(f"{nw} young shop(s) with 100+ sales")
    else: reasons.append("no young shop with 100+ sales seen on page one")
    med = [k["price_median"] for k in kws if k["price_median"]]
    if med:
        m = statistics.median(med)
        if our_price <= m * 1.15: score += 1; reasons.append(f"our ${our_price} is within ~15% of the market median ${m:.2f}")
        else: reasons.append(f"our ${our_price} is well above the market median ${m:.2f}: price risk")
    label = "Higher" if score >= 4 else "Medium" if score >= 2 else "Lower"
    return {"design": design, "sell_likelihood_heuristic": label, "score": score, "reasons": reasons}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-keyword", type=int, default=50)
    ap.add_argument("--only")
    args = ap.parse_args()
    cfg = json.loads((HERE / "keywords.json").read_text())
    shop_cache, out, verdicts = {}, {}, []
    for design, d in cfg["designs"].items():
        if args.only and design != args.only:
            continue
        kws = [analyse_keyword(k, args.per_keyword, shop_cache) for k in [d["slogan"]] + d["keywords"]]
        out[design] = kws
        verdicts.append(verdict(design, kws, cfg["our_price"]))
        print(design, verdicts[-1]["sell_likelihood_heuristic"])
    (HERE / "results.json").write_text(json.dumps(out, indent=1))
    lines = ["# Etsy benchmark (live API data)", "", f"Generated {time.strftime('%Y-%m-%d')}. Heuristic verdicts rank risk; Etsy exposes no per-listing sales.", "",
             "| Design | Heuristic | Why |", "|---|---|---|"]
    for v in verdicts:
        lines.append(f"| {v['design']} | {v['sell_likelihood_heuristic']} | {'; '.join(v['reasons'])} |")
    lines += ["", "## Top listings by favourites, per keyword", ""]
    for design, kws in out.items():
        lines.append(f"### {design}")
        for k in kws:
            lines.append(f"- **{k['keyword']}**: {k['total_results']} results, median ${k['price_median']}, new-shop share {k['new_shop_share']}")
            for r in k["top_by_favorers"][:3]:
                lines.append(f"  - {r['favorers']} favs, ${r['price']}, shop sales {r['shop_sales']}, rating {r['shop_rating']}: {r['title'][:80]}")
        lines.append("")
    (HERE / "REPORT.md").write_text("\n".join(lines))


if __name__ == "__main__":
    main()
