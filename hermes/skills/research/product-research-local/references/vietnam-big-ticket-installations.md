# Vietnam Big-Ticket Installations (references)

Purchasing-research conventions for large VN installations/services (home lifts, solar, aircon,
kitchens) — extends `product-research-local` from retail items to contract work. Learned on the
HCMC home-lift comparison (2026-08-12).

## Money & units

- VND units: "triệu"/"tr" = million, "tỷ" = billion, "đồng"/"VNĐ"/"đ" = dong. Fact-mining regex:
  `[\d.,]+\s*(?:triệu|tr\b|trieu|đồng|vnđ|VND|tỷ|ty)\b`. "Từ X triệu" = entry-point price.
- Construction specs in mm: `\d[\d.,]*\s*[x×]\s*[\d.,]+\s*mm`.

## Market-structure shorthand

- "liên doanh" = locally assembled with imported components (mid tier); "nhập khẩu" = fully
  imported (premium tier). Price tiers track this split, not the technology. Example (installed
  5-stop home lifts, Aug 2026): local traction 250-400 triệu; liên doanh 400-800 triệu; fully
  imported 600 triệu - 1.2 tỷ, imported hydraulic at the top of the range.

## Vendor-site scraping reality

- Many VN installer/vendor sites block scrapers — web_extract returns empty / "(no title)":
  kalealifts.com.vn, cibeslift.com.vn, thangmaytaza.com, thangmaythiennam.net, cauthangmay.com,
  giathangmaygiadinh.com. Cite those at title level and flag, or mine the web_extract cache file
  (full text at `<cache>/web/<host>-<hash>.md`) if partial content landed.
- Sites that DO render (verified Aug 2026): thangmayght.com, thangmaygde.com, thangmaynidec.vn,
  getis.vn, tns-lift.com.vn, vnexpress.net, otosaigon.com threads.
- Global brands with official VN entities (check FIRST for product specs): kone.vn,
  otis.com/vi/vn, tkelevator.com/vn-en, hyundaielevator.com.vn, mitsubishielectric.com.vn.
  Dealer-distributed brands (Mitsubishi, Schindler, Fujitec) need local-entity verification
  before promising warranty.

## Standards & legal lookup (regulatory claims)

- tieuchuan.vsqi.gov.vn = official TCVN catalogue (reliable search for exact standard numbers);
  thuvienphapluat.vn / luatvietnam.vn for circulars/decrees (thuvienphapluat 403s curl — use
  Wayback per the no-key-web-research skill, Rung 3).
- TCVN 6396-xx maps to EN 81-xx (e.g. TCVN 6396-20:2017 = EN 81-20:2014; TCVN 6396-41:2018 =
  EN 81-41:2010 IDT). Scope trap: the marketing name may not match the standard's scope (EN 81-41
  "home lift" = ≤0.15 m/s platform lifts, NOT a passenger lift) — verify the governing standard.
- Safety regime: equipment on the strict-safety list (Thông tư 36/2019/TT-BLĐTBXH) requires
  periodic inspection (kiểm định) per Thông tư 12/2021/TT-BLĐTBXH — insist the quote includes it.

## Cross-check discipline

- Prices are vendor-published → cross-check across ≥3 independent installers before stating a
  range. Vendor price TABLES (technology-vs-price) are the best single source but self-serving.
- Vendor pages rarely publish the space figures that decide the purchase (shaft/pit/overhead
  drawings, machine-room needs) — the final deliverable should list the exact items to request in
  written quotes (fit drawing for the given footprint, pit depth, top-landing overhead, kiểm định
  fee, warranty terms).

## User rules (durable)

- Only brands with official VN availability + local warranty (no parallel imports) — applies to
  installations too, not just retail electronics.
- For market/purchasing research, the user accepts a web+industry-heavy source ratio (web=45,
  industry=40, academia=10, github=5 @ N=120, chosen 2026-08-12).
