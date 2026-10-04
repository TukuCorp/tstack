"""Compact stdin parser for the Tiki.vn product-search API.

Usage:
  curl -s "https://tiki.vn/api/v2/products?q=<query>&limit=30" \
       -H "Accept: application/json" -A "<desktop-UA>" | python tiki_parse.py

Why: the full API response is ~100KB+ and gets truncated mid-JSON by terminal
output caps if you try to capture it whole; parsing in-shell keeps the output
to a few compact lines per product.

Notes:
- Tiki rate-limits after ~8-10 rapid calls: the endpoint starts returning an
  anti-bot HTML page (HTTP 200, not JSON) -> you'll see "JSON_ERR ... line 1
  column 1 (char 0)". Pace calls (sleep 1-2s) and/or fall back to the browser
  at https://tiki.vn/search?q=<term> (different IP).
- Tiki search matches LOOSELY: for brands with no real products it returns
  hundreds/thousands of unrelated items. Never trust the TOTAL count; check
  the returned names/brand field, and on the browser page check the
  "Thuong hieu" (brand) filter facet - if the brand isn't a facet, it has no
  products on Tiki.
"""
import sys
import json

try:
    d = json.load(sys.stdin)
except Exception as e:
    print("JSON_ERR", e)
    sys.exit(0)

items = d.get("data", [])
print("TOTAL", d.get("paging", {}).get("total", "?"))
for it in items:
    name = (it.get("name") or "").replace("|", " ")[:62]
    seller = (it.get("seller_name") or "")
    brand = (it.get("brand") or "")
    print(f"{name} || {seller} || {brand} || {it.get('price')}")
