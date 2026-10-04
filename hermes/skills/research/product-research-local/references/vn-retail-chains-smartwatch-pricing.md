# VN retail-chain smartwatch pricing & availability (verified Aug 2026)

Method: direct urllib fetches (desktop UA, vi-VN Accept-Language) of thegioididong.com,
cellphones.com.vn, hoanghamobile.com, fptshop.com.vn, antien.vn, amazfit.com.vn, mi.com/vn,
fossil.com.vn + Tiki API, all parsed with Python regex/JSON in execute_code. User context:
VN buyer, budget ≈ 6.5M VND, wants local warranty, hybrid/health-focused models.

## Officially available with local warranty (VND)

| Model | VN price | Official store / URL | Warranty |
|---|---|---|---|
| Garmin Venu Sq 2 | 6.372.000 | An Tiên (dealer) — antien.vn/garmin-venu-sq-2.html | chính hãng |
| Garmin Vivoactive 5 | 5.690.000 | TGDĐ — thegioididong.com/dong-ho-thong-minh/garmin-vivoactive-5-day-silicone | 24 tháng (TGDĐ) |
| Garmin Vivoactive 6 | 7.320.000 (TGDĐ) / 8.290.000 (HoangHa) | TGDĐ …/garmin-vivoactive-6 | 24 tháng |
| Garmin Forerunner 165 | 3.990.000 | TGDĐ / CellphoneS / HoangHa / An Tiên | 24 tháng (TGDĐ), BH 12T (CPS) |
| Garmin Forerunner 165 Music | 5.490.000 | HoangHa | chính hãng |
| Garmin Venu 3 (45mm / 3S) | 9.830.000 | TGDĐ …/garmin-venu-3-day-silicone | 24 tháng |
| Amazfit Active 2 | 2.490.000 (HoangHa) / 2.990.000 (amazfit.com.vn) | HoangHa + amazfit.com.vn/products/amazfit-active-2 | 12 tháng |
| Amazfit Balance | 3.890.000 (HoangHa) / 5.990.000 (amazfit.com.vn) | HoangHa + amazfit.com.vn/products/amazfit-balance | 12 tháng |
| Amazfit Balance 2 | 6.990.000 (HH) / 7.490.000 (TGDĐ) / 7.990.000 (amazfit.com.vn) | HoangHa / TGDĐ | 12 tháng |
| Amazfit GTR 4 | 3.590.000 | HoangHa only (EOL at TGDĐ + amazfit.com.vn) | chính hãng |
| Xiaomi Watch S4 | 3.480.000 (TGDĐ) / 3.490.000 (CPS) / 3.79–4.59M (HH variants); MSRP 4.290.000 (Xiaomi VN FB) | TGDĐ / CPS / HoangHa; mi.com/vn | 12 tháng |

## EOL / replaced (Aug 2026)

- **Huawei Watch GT 5** — TGDĐ product page shows `item_web_status: "Ngừng kinh doanh"`; absent
  from FPT + HoangHa. Current gen: Huawei Watch GT 6 (4.390.000₫ HH/TGDĐ), Huawei Watch 5
  (6.69–6.99M).
- **Garmin Venu Sq 2** — dropped from TGDĐ/CPS/FPT lineups (Venu 4 is current, 14.240.000₫);
  still officially sold via dealer An Tiên at 6.372.000₫.
- **Amazfit GTR 4** — not on amazfit.com.vn or TGDĐ (EOL); HoangHa still clearing official stock
  at 3.590.000₫ (≈30% under what amazfit.com.vn would list — old-stock clearance pattern; always
  cross-shop chains vs brand store).

## Import-only (no official VN warranty) — evidence trail

- **Withings ScanWatch 2 / Lite / Nova**: Tiki API q=Withings → 0 items; `site:lazada.vn Withings`
  → unrelated junk; 0 hits at TGDĐ/FPT/CPS/HoangHa; Withings support (support.withings.com) states
  Asia availability = Hong Kong only (medical-certified markets); ScanWatch exchange program
  excludes Asia outside HK. VN buyers parallel-import (FB smartwatch groups).
- **Citizen CZ Smart**: US-market model; no VN chain carries it (TGDĐ only published launch news);
  VN watch resellers (e.g. giaynhatchinhhang.vn) parallel-import. Citizen VN lineup = analog only.
- **Fossil Gen 6 Hybrid**: Fossil exited smartwatch production (2024); official fossil.com.vn
  (stores: Vincom Đồng Khởi Q1 + Vạn Hạnh Mall Q10, HCMC) sells analog/automatic only.
- **Skagen Jorn Hybrid HR**: no official VN channel; Tiki carries only analog Skagen via reseller
  (Bluefish Shop).

## Budget fit (user ≈6.5M VND)

In budget: FR 165 (3.99M), Vivoactive 5 (5.69M), Venu Sq 2 (6.37M), Active 2 (2.49M), Balance
(3.89M HH), GTR 4 (3.59M), Watch S4 (3.48M). Over budget: Vivoactive 6 (7.32M), Venu 3 (9.83M),
Balance 2 (6.99M+).

## Per-site parse recipes (exact patterns used)

- TGDĐ category card: `<li class="item ..." data-name="Garmin Venu 4 45mm dây silicone"
  data-price="14240000.0">` + `<strong class="price">14.240.000&#x20AB;</strong>` → regex
  `data-name="([^"]*)"[^>]*data-price="([0-9.]+)"`, html.unescape name, strip `&#x20AB;`.
- TGDĐ product page price: `class="(?:box-price|price|price-old)"[^>]*>\s*([0-9][0-9.]{2,12})\s*&#x20AB;`
  → [promo, list].
- TGDĐ EOL: grep for `information-oldProduct` / `Ngừng kinh doanh`.
- HoangHa: `window\.insider_object\.listing = (\{.*?\});` → json.loads → items[]: name,
  unit_sale_price (float, may be null → check unit_price), url. Beware prices like `6830000.0`.
- CellphoneS: split `<tr>` rows of `seo-table seo-product-price`, cells are Tên sản phẩm | Giá bán
  | Giá thu cũ lên đời; strip `đđ` suffix.
- FPT product page: `"price"\s*:\s*"?([0-9.]+)"?` from embedded JSON (e.g. FR 970 = 17670000,
  Watch S5 = 4890000). Category page has no prices.
- amazfit.com.vn (Shopify): `og:price:amount" content="([^"]+)"` or `"price": 2990000`.
- antien.vn: `<div class="item-product">` → `<a class="title" href="/dong-ho-<slug>.html">NAME</a>`
  + `<span class="price">6.830.000 ₫</span>`.
