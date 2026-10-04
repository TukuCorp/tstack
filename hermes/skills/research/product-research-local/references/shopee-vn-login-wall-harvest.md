# Shopee VN login-wall harvest — worked example (wired IEMs, Aug 2026)

Task: find popular wired IEMs (tai nghe có dây) ≤ ~1.2M VND on shopee.vn with prices, sellers, ratings, sold counts.

## Access status confirmed this session (all FAILED — do not retry fresh)
- Browser (search + product pages): "Login Required" wall
- API v4/v2 (search_items, item/get, pdp/get_pc): 403 + `{"error": 90309999, "is_login": false}` — even with homepage cookie jar, Referer, `x-api-source: pc`
- `/product/<shopid>/<itemid>` share format: 200 but same 161,177-byte JS shell; zero og:/JSON-LD/meta product data
- `m.shopee.vn`: connection fails; `r.jina.ai` reader: same login wall
- Shop pages (`shopee.vn/shop/<id>`): shop names NOT indexed by search engines

## What worked
1. **Bing RSS** (urllib/curl, desktop UA): `https://www.bing.com/search?q=site:shopee.vn+Moondrop+Chu+2&format=rss&count=25`
   → 17 unique live product URLs across ~23 queries, ~1s spacing. No rate-limit hit.
2. **DDG HTML**: worked for the first query batch (6 URLs incl. Moondrop Nice Buds,
   Aria 2, Chu 2, Quarks DSP), then `anomaly.js?cc=botnet` block. Use first, sparingly.
3. **Google**: `/sorry` CAPTCHA page in browser. **Mojeek / Ecosia**: 403 via curl.
4. **Liveness check**: `curl https://shopee.vn/product/<shop>/<item>` → 200 + ~161,177B shell = live; 404 = delisted. (Same shell regardless of product — it's a login-wall shell, not the product page.)
5. **Prices**: scraped same-SKU cards from server-rendered VN specialist retailers (regexes below). Two independent retailers agreed within ~10% on every model checked.

## Retailer card regexes (Python, DOTALL)
```python
# tainghe.com.vn /brand/<slug> — Xuân Vũ Audio (HCMC)
<li class="item"> ... <a class="p-name">NAME</a> ... <span class="p-price">(\d[\d.]*)đ</span>
# stock: <span class="status_contact"> Tạm hết hàng / còn hàng

# taingheviet.com /category/<slug> — SLaudio (WordPress-style)
<div class="product__title text-center my-2">NAME</div> </a>
<div class="product__price text-center mb-4"><span class="mx-1 text-16">650.000 VNĐ</span>
# product URLs: taingheviet.com/<slug>-pr<id>.html ; site search: /?s=<q>

# songlongmedia.com (WooCommerce) — prices as plain text "1.490.000"
```

## Price cross-check table (VN retailers, VND)
| Model | Xuân Vũ Audio | SLaudio | Song Long |
|---|---|---|---|
| Moondrop Nice Buds | 165.000 | 200.000 | — |
| Moondrop Chu 2 DSP | 670.000 | — | — |
| Moondrop Aria 2 | 1.890.000 | — | — |
| 7Hz Salnotes Zero | — | 650.000 | — |
| 7Hz Zero 2 (Crinacle) | — | 550.000 | — |
| Truthear Gate (mic) | 530.000 | 490.000 | — |
| Truthear Zero Red | 1.099.000 | — | — |
| Truthear Zero Blue 2 | 1.45–1.59M | 1.49–1.59M | — |
| Truthear HEXA | 1.490.000 | 1.990.000 | 1.490.000 |
| KZ EDX Pro / EDC Pro | 190–250.000 | — | — |
| KZ ZSN Pro 2 (mic) | 500.000 | — | — |
| KZ ZS10 Pro 2 (mic) | 990.000 | — | — |
| FiiO FD11 (mic) | 1.250.000 | 1.250.000 | — |
| FiiO JD1 | 500.000 (OOS) | 550.000 | — |
| Tangzu Wan'er SG 2 (mic) | 550.000 | 450–590.000 | — |
| Tangzu Yu Xuan Ji | 1.190.000 (OOS) | 1.250.000 | — |

## Seller identification from slugs
- `[NC]` prefix → **Nghe Tạp** (HCMC audiophile store; shop id 79953810)
- "Chính hãng phân phối" → official VN distributor (Truthear shop 689965329 — Mall-badge candidate)
- "Chính hãng Bảo hành 12T" → authorized warranty store (Moondrop shop 134240781)
- Official store pages: `site:shopee.vn <brand> "official store"` → KZ Official Store = shopee.vn/kzofficialstore.vn
  (only confirmed official store found; none for 7Hz/Tangzu/FiiO/Moondrop/Truthear)

## Deliverable pattern for login-walled platforms
- Verified product URLs (state how verified) + benchmark prices clearly labeled "retailer reference,
  Shopee usually equal or 5–15% lower" + `n/a (app-only)` for rating/sold-count/Mall-badge
- Flag over-budget items explicitly; note category best-sellers from community reputation,
  never fabricate scraped counts
