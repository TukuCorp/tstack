# French premium baby brands — availability in Vietnam (verified Aug 2026)

Worked example of the OFFICIAL / PARALLEL / RARE-ABSENT verdict framework for the
Tuku household's "what to import from France" question.

## Method used per brand

1. **Tiki**: JSON API (`tiki.vn/api/v2/products?q=<brand>`) + browser search page
   (`tiki.vn/search?q=<brand>`) for the API-blocked tail of the list.
2. **Lazada**: browser on `lazada.vn/catalog/?q=<brand>` — page-1 relevance scan +
   console JS title scan for brand tokens.
3. **Shopee**: search-engine harvesting of indexed `shopee.vn/...i.<shopid>.<itemid>`
   URLs (Brave curl — worked intermittently; DDG html — one success; Bing RSS — junk;
   direct Shopee = login-walled).
4. **Official check**: grep brand domains (petit-bateau.com, jacadi.fr, absorba.com)
   for `vietnam|hanoi|ho chi minh|saigon` → none contained any.

Key pitfall observed everywhere: **platform search counts are loose**. Tiki returned
64–2000 "hits" for absent brands (books, supplements, wigs, manga); Lazada returned
2,700–4,100 for every query. Real brand items appear at the TOP of the first page when
they exist (Sophie la Girafe did; the rest didn't).

## Verdict table

| Brand | Category | Verdict in VN | Evidence (platform → what came back) | Notes |
|---|---|---|---|---|
| Petit Bateau | Clothing | RARE/ABSENT | Tiki: 64 hits, ALL false positives (FR books, Boube OEM, Le Petit Marseillais). Lazada: 3,600 loose, no real item p1. Brave site:shopee: 0. petit-bateau.com: no VN mention | No official channel found; strong import candidate |
| Jacadi | Clothing | PARALLEL-only (tiny) | Tiki: only hair-fringe wigs. Lazada: 3,705 loose, 0 real on p1 (console scan). Brave: real Shopee listing "Áo Bé Gái Jacadi Paris – Hàng Xuất Dư Chính Hãng" (shop `309hwiklshop.vn`); ubuy.vn brand page exists; jacadi.fr no VN | No boutique / distributor / LazMall found; one-off resells only ("hàng xuất dư" = brand surplus) |
| IKKS Baby | Clothing | RARE/ABSENT | Tiki: no products rendered. Lazada: 4,177 loose, 0 real p1 (fishing lines/gamepads). Brave/DDG: 0 | — |
| Catimini | Clothing | RARE/ABSENT | Tiki: 0 results. Brave/DDG: 0 | — |
| Tartine et Chocolat | Clothing | RARE/ABSENT | Tiki: only chocolate food brands (Beryl's etc.). Brave/DDG: 0 | — |
| Cyrillus | Clothing | RARE/ABSENT | Tiki: 0 results. Brave/DDG: 0 | — |
| Vertbaudet | Clothing | RARE/ABSENT | Tiki: only male-supplement listings. Brave/DDG: 0 | — |
| Absorba | Clothing | RARE/ABSENT | Tiki: only laptop bags. Lazada: 3,244 loose, 0 real (only "Absorb" pet wipes). absorba.com no VN | — |
| Moulin Roty | Toys | RARE/ABSENT | Tiki: 0 results. Lazada: 2,718 loose, 0 real (cheese/mustard junk). Brave: 0 | Top import candidate |
| Djeco | Toys | PARALLEL-only (1 item) | Tiki: air-purifiers only (loose "djeco" match). Lazada: 3,251 loose, ONE real item "Đồ Chơi Trẻ Em Djeco Chú Gấu Khoác Quần Áo Mới" 479k₫ — Hong Kong LazGlobal seller | Cross-border only; newborn-range items effectively unavailable |
| Janod | Toys | PARALLEL-only (thin) | Lazada: real "Bản đồ thế giới nam châm Janod" ×2 (~1.3–1.5M₫, 51% off) — South Korea LazGlobal sellers. Tiki: 0 | Cross-border only |
| Sophie la Girafe | Toys | PARALLEL (widely) | Lazada: 3,903 products, REAL items incl. Eau de Soin newborn perfume 1.765k₫ (103 sold, HCMC seller), EDT, Fanfan fawn teether 900k₫; also Shopee indexed listing ("Bộ sản phẩm nước hoa Sophie La Girafe"); Vietnamese term "hươu cao cổ Sophie" works | AVAILABLE locally — skip importing. VN term: hươu cao cổ Sophie |
| Kaloo | Toys | RARE/ABSENT | Tiki: fucoidan supplements only. Lazada: 3,560 loose, 0 real. Brave: 0 | Import candidate |
| Vilac | Toys | RARE/ABSENT | Tiki: fertilizer only; brand facet list (Greenhome/VIFUSA/…) confirms no Vilac. Brave/DDG: 0 | — |
| Nathan | Toys | RARE/ABSENT | Tiki: only books by author "Nathan Furr" (no French Nathan éditions toys). Brave/DDG: 0 | — |
| Doudou et Compagnie | Toys | RARE/ABSENT | Tiki: only French-language books. Brave/DDG: 0 | — |
| Petit Ours Brun | Books | RARE/ABSENT | Tiki: no POB books (only Le Petit Prince / Le Petit Nicolas from Librairie française de Hanoi) | French books only via niche FR bookstores (see below) |
| T'choupi | Books | RARE/ABSENT | Tiki: only "Chubby" stationery (loose match) | Same |

## Bottom line for the parent

**DEFINITELY WORTH IMPORTING (absent in VN — no official, no consumer-visible parallel supply):**
Petit Bateau, IKKS Baby, Catimini, Tartine et Chocolat, Cyrillus, Vertbaudet, Absorba (clothing);
Moulin Roty, Kaloo, Vilac, Nathan, Doudou et Compagnie (toys); Petit Ours Brun, T'choupi (books).
Jacadi / Djeco / Janod: only 1–2 cross-border (LazGlobal KR/HK) or surplus listings — still worth
importing for selection/price.

**AVAILABLE IN VN (buy locally, skip):** Sophie la Girafe (Lazada/Shopee, HCMC resellers).

## Useful VN-domain facts found

- French-language book sellers on Tiki: "Librairie française de Hanoi", "Blue Horizon Books",
  "Nhà sách Fahasa" (FR books section) — the only local channel for French children's books.
- Cross-border import services that list brands for VN delivery (a "possible via cross-border"
  signal, not local stock): ubuy.vn, wulao.vn (also fado.vn in general VN import circles).
- Reseller vocabulary: "hàng xuất dư" (brand surplus/overstock), "hàng xách tay" (personal import),
  "chính hãng" (genuine). "Hàng xuất dư chính hãng" = surplus genuine goods (e.g. the Jacadi listing).
