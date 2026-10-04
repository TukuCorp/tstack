---
name: no-key-web-research
description: "Use when web research hits credit errors or 403 blocks, or for VN hospital/doctor research (see references/vn-hospital-doctor-research.md)."
---

# No-Key Web Research (fallback chain when paid search/scrape backends are unavailable)

When `web_search`/`web_extract` fail with credit errors, or a target site returns 403 (Cloudflare), do NOT give up or fabricate. Work the chain below — every rung uses plain HTTP + public archives, no API keys. Fallback order: DDGS → Bing scrape → Wayback CDX discovery + snapshot fetch → official PDF extraction.

## /research --depth exhaustive integration
When the `research` skill's `scripts/wide_pass.py` reports `firecrawl: unavailable` (no FIRECRAWL_API_KEY), fill the industry/web buckets with the `web_search` tool FIRST — it can be live even without the key (verified 2026-08) — then WebFetch seed lists, then this skill's chain. Full wide-pass ops (helper per-run cap quirk, OpenAlex noise, ledger finalization recipe incl. ledger-write safety, web_extract cache-mining, URL/DOI normalization guards, repo-signal verification) are in [references/research-exhaustive-ops.md](references/research-exhaustive-ops.md).

## Rung 1 — DDGS (DuckDuckGo) via the Hermes venv
- CLI: `ddgs text -k "query" -m 6` (flag is `-k`/`--keywords`, NOT `-q`).
- Python API (more control): `C:/Users/tukum/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe` with `from duckduckgo_search import DDGS` — note the import name is `duckduckgo_search` even though the CLI/package is now `ddgs`.
- Pitfalls (all hit in practice):
  - **Rate-limits fast**: after ~3-5 batches it returns EMPTY result lists. Sleep 8s+ between queries, drop to 2-3 queries per run, or use `backend="lite"`.
  - **Vietnamese-language queries return garbage** (Wikipedia "Phân" = feces, unrelated news sites). Use English queries or exact legal-document names ("Thông tư 40/2021/TT-BTC") instead of long Vietnamese phrases. The `region` param doesn't fix this.
  - **Disambiguate a bare VN noun before domain research**: a short query (often a voice transcription) can map to unrelated domains, so run a `<term> là gì` definition search first and confirm the entity with the user before researching prices or details — otherwise the whole run targets the wrong domain.
  - DDG result hrefs may be `duckduckgo.com/l/?uddg=<real-url>` redirects — urldecode and strip.

## Rung 2 — Bing scrape
`requests.get("https://www.bing.com/search?q=" + quote(q))` + regex `<h2><a href="([^"]+)"[^>]*>(.*?)</a></h2>`. Works intermittently; Bing serves a JS/consent wall on other attempts. Never rely on it alone.

## Rung 2b — News RSS feeds (best for dated news briefs) ⭐
When the ask is "news from the past N days", skip scraping and hit news RSS — machine-readable, dated `<item>`s, no keys:
- **Google News RSS** (best for Vietnamese/local freshness; returns up to 100 dated items):
  `curl -s "https://news.google.com/rss/search?q=<urlencoded>&hl=vi&gl=VN&ceid=VN:vi"` — set `hl=en&gl=US&ceid=US:en` for English. Filter by pubDate yourself.
- **Bing News RSS**: `curl -s "https://www.bing.com/news/search?q=<q>&format=rss" -A "Mozilla/5.0 ..."` — fewer items and mixes in stale ones; filter by pubDate. Links are apiclick redirects.
- Parse: `re.findall(r'<item>(.*?)</item>', t, re.S)` then extract `<title>/<pubDate>/<link>`, `html.unescape` titles. Google News item links are news.google.com redirects — fine for headline+date triage; fetch the source site separately for full text.
- **Locale matters**: for Vietnamese company news the English query (`q="Kinh Bac City KBC"`, `hl=en`) returned 0 items while the Vietnamese one (`q="KBC Kinh Bắc"`, `hl=vi&gl=VN&ceid=VN:vi`) returned 100 fresh items. Use the target language's locale + query.
- Pitfall: DDGS `.news()` can 403 Ratelimit outright (not just empty lists) — go straight to RSS for news queries.
- Worked 2026-08-05: Firecrawl out of credits + DDGS 403 → Google News RSS delivered all KBC Q2-results stories with dates in one call.
- **Google News RSS redirect links (`news.google.com/rss/articles/...`) return HTTP 400 to curl** even with cookie jar + `?hl=vi&gl=VN&ceid=VN:vi` — treat them as headline+date triage ONLY. To get the real article URL, query **Bing News RSS** and decode:
  `curl -s "https://www.bing.com/news/search?q=<q>&format=rss&setlang=vi" -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"` → each `<link>` is `bing.com/news/apiclick.aspx?ref=FexRss&...&url=<urlencoded-real-url>` — urldecode the `url=` param → real article URL → curl the source site directly (most VN news sites serve plain HTML to curl: tuoitre.vn, vnexpress.net, dantri.com.vn, thanhnien.vn, kenh14.vn all returned 200 with a browser UA, 2026-08-06).
- If Bing News RSS doesn't surface the article, search tuoitre.vn directly (SSR search — see Rung 6).

## Rung 2c — PubMed eutils (no-key literature citations) ⭐
When a research brief needs real paper citations and web_search is down, PubMed eutils is key-free for modest use:
- Search: `curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=<urlencoded>&retmax=6&sort=relevance"` → `<Id>34913204</Id>` entries.
- Metadata: `curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id=<ids comma-separated>&retmode=json"` → JSON with title, pubdate, journal, elocationid (DOI).
- Worked 2026-08-06: pulled 2 systematic reviews on phenol matricectomy (JEADV 2022, Acta Derm Venereol 2020) with PMIDs + DOIs in one round-trip — enough to anchor treatment claims with tier-3 citations.

## Rung 3 — Wayback CDX: URL discovery for bot-blocked sites ⭐ (the key trick)
Sites like thuvienphapluat.vn 403 curl/requests even with full browser headers, but the Wayback Machine has snapshots. The CDX API exposes the **exact original URLs** you can't discover any other way:
```
http://web.archive.org/cdx/search/cdx?url=thuvienphapluat.vn/van-ban/Thue-Phi-Le-Phi/Thong-tu-40-2021*&output=text&collapse=urlkey&limit=6&fl=original,timestamp,statuscode
```
- `*` wildcards work in the path. `collapse=urlkey` dedupes. Pick a snapshot with `statuscode 200`.
- Use this for ANY blocked domain (VN legal portals, law-firm sites, paywalled article shells).
- CDX quirks (hit 2026-08-06): **wildcard domain-prefix queries** (`url=bvdalieutphcm*`) return 403 "This type of CDX query requires authorization" — use `matchType=domain&url=bvdalieutphcm.vn` instead. CDX intermittently 503s or returns empty for the same query — retry after a few seconds. `&filter=original:.*lieu.*` narrows by URL substring.

## Rung 4 — Fetch snapshots: `id_` + gzip handling ⭐
```
curl -sL --compressed -A "Mozilla/5.0 ..." "https://web.archive.org/web/<timestamp>id_/<full-original-url>" -o out.html
```
- The `id_` suffix returns the original page HTML (no wayback banner).
- **`--compressed` is mandatory** — without it wayback serves gzip bodies that save as binary garbage (looks like `\b\u0000\u0000is` at the top).
- Python `requests` auto-decompresses, so in scripts just use requests.

## Rung 5 — Official PDFs for primary sources
- Legal documents: try the issuing body's official PDF first (e.g., `baohiemxahoi.gov.vn` hosted the official Luật BHXH 2024 PDF — curl worked where every portal 403'd). Extract with pymupdf: `import fitz; "\n".join(p.get_text() for p in fitz.open(f))`.
- Grep the extracted text for the exact article headings (`Điều 2. Đối tượng...`) and quote verbatim — never paraphrase a statute you haven't read from the primary text.

## Rung 6 — Vietnamese site & directory quirks (tested 2026-08-06)
- **News-site search**: tuoitre.vn search is SSR — `https://tuoitre.vn/tim-kiem.htm?keywords=<q>` returns article hrefs like `/slug-20251003130332013.htm` that parse directly. vnexpress.net/tim-kiem, dantri.com.vn/tim-kiem, and 24hmoney.vn/tim-kiem are JS shells/blocked (27–539 bytes, no article links in HTML); thanhnien search HTML has no article links → route those through Bing News RSS (Rung 2b), which resolves real article URLs via the `url=` param of `bing.com/news/apiclick.aspx` links (verified 2026-08-07 for danviet.vn + KBC stories).
- **Doctor aggregators**: bookingcare.vn is server-rendered → curl-parseable; profile pages carry "X năm kinh nghiệm" claims good for cross-checking hospital bios. youmed.vn is a JS SPA (no `__NEXT_DATA__`, no content in HTML) → skip.
- **VN pharmacy / dược-liệu product pages are JS shells**: caythuocdangian.vn articles, pharmacity.vn dược-liệu pages, and nhathuoclongchau.com.vn thành-phần pages return chrome-only HTML to curl even with a browser UA (no price or body content) — read prices via browser-control, never static curl.
- **Hospital doctor directories**: parse the `<option value>` filter map first, then query the dept-filtered listing (e.g. `tamanhhospital.vn/chuyen-gia/?filter_chuyenkhoa=432&filter_diadiem=36`), then each `/chuyen-gia/<slug>/` profile for stated years ("X năm kinh nghiệm"). Note: a hospital's department may have its own site on a different domain (UMC's derm dept = dalieudhyd.vn while umc.edu.vn rejects curl with 400 Invalid Hostname).
- **Dead hospital domains**: probe `.vn / .com.vn / .org.vn / .gov.vn` variants; if all dead, Google News RSS the hospital name — rename announcements surface there (e.g. BV TP Thủ Đức → BV Đa khoa Thủ Đức, 08/2025).
- Full playbook with verified URL inventory: `references/vn-hospital-doctor-research.md`.

## Rung 7 — Flight schedules: skip the metasearch UIs, hit the schedule sites (verified Aug 2026)
When the ask is "find/rank flights on route X–Y for date D" (business travel, same-day returns):

- **Google Flights UI is hostile to automation**: the date picker reverts programmatic input — typing into the Departure/Return textboxes works, but a subsequent `Done` click (or any calendar interaction) resets both dates to defaults; setting input values via JS + dispatching input events doesn't commit to the search state either. Its natural-language URL (`https://www.google.com/travel/flights?q=Flights+from+SGN+to+HPH+on+2026-08-10+through+2026-08-10`) resolves the ROUTE fine but ignores the dates. Skyscanner serves a CAPTCHA; Kayak errors with `errorOccurred=true`.
- **Use flightsfrom.com instead**: `web_extract` on `https://www.flightsfrom.com/SGN-HPH` returns the full weekly timetable — per-airline (VietJet/Vietnam Airlines/others), flight numbers, departure times per weekday, flight duration — plus a monthly calendar with per-day flight counts. Mirror route `https://www.flightsfrom.com/HPH-SGN` for returns. `web_extract` succeeds where the metasearch UIs fight back.
- Then rank same-day round-trip combos by on-ground time (arrival → next departure) and note the airline (full-service vs LCC) — e.g. for a morning kickoff + same-day return: outbound 09:00 + return 16:25 gives ~5h on ground.
- Caveat to report honestly: timetable ≠ availability/pricing for the specific date; the schedule pages are the daily pattern, not booked inventory.

## Rung 8 — Hi-res originals: WordPress media API + CDN 404-stub check
When the ask is a larger copy of an image already found small:
- **WordPress sites**: query `https://<site>/wp-json/wp/v2/media?search=<slug>&per_page=10` — each hit lists `width x height` plus every generated size with direct URLs. The `full` size is the ceiling; if it matches what you have, no larger copy exists on that host — stop, don't retry.
- **CDN throttling vs deletion**: identical tiny responses (e.g. 153 bytes) across hosts, referers, and spaced retries mean the file was deleted upstream, not throttled. Check `size_download` before burning retry loops; purge the stubs so they aren't mistaken for real files.
- **Variant hunting**: same slug often exists as `.jpg/.png/.avif` or dated re-uploads (`/2021/05/` vs `/2024/03/`) — grep the homepage HTML for `uploads/` URLs filtered to the topic before concluding nothing bigger exists.

## Workflow hygiene
- Save every fetched source as `<key>.txt` in a per-session fetch dir (`research/vn_law_fetch/` style) so verbatim quotes are re-verifiable.
- Clean HTML with bs4 if available, else regex-strip `<script>/<style>` then tags, then html.unescape.
- **Windows curl path trap**: native curl.exe writes `/tmp/...` to the C: drive root, not MSYS /tmp — always use relative paths under the workdir.
- Some portals (luatvietnam.vn) return 300K of nav junk with the real content elsewhere — prefer official PDFs or thuvienphapluat wayback snapshots for statute text.

## Scripts
- `scripts/wayback_lookup.py` — CDX discovery + snapshot fetch for blocked sites (run with the venv python).

## Output conventions (this user)
- Research briefs: save to `~/Downloads/remote/research/YYYY-MM-DD_<topic>.md`, deliver via MEDIA: link + a chat summary.
- Vietnamese-language topics → write the brief in Vietnamese (see also `vietnam-employment-compliance` skill for the VN legal domain).
