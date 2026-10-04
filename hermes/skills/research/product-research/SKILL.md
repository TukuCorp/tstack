---
name: product-research
description: Research products with credible-source verification (Wirecutter/Rtings/Crinacle/medical sources) + optional local market availability checks. Covers global "best X under $Y" research, direct-access fallbacks when search backends are down, and Vietnamese e-commerce discovery.
---

# Product Research (with local availability verification)

Use when the user asks you to find products for a specific need AND check if they're available in a specific market (especially Vietnam/HCMC).

## Workflow

### Phase 1: Parallel dispatch

Dispatch **two subagents simultaneously** via `delegate_task` (tasks array):

**Subagent A — Product & brand research**
- Search credible medical/consumer sources (Mayo Clinic, AAOS/OrthoInfo, NHS, WebMD, Consumer Reports, Amazon best-sellers)
- Identify specific product categories, brands, model names
- Focus on evidence-backed, well-reviewed items
- Return specific names, ratings, prices (USD)

**Subagent B — Local availability in target market**
- Search local e-commerce platforms using local-language search terms
- Focus platforms in priority order: Tiki (most accessible), Lazada (accessible), Shopee (blocked — see pitfalls)
- Use Vietnamese terms for baby/medical products (địu vải, viêm gân, nẹp cổ tay, etc.)
- Return prices (VND), seller locations, delivery times, units sold

### Phase 2: Compile

Build a ranked comparison table with:
- Product name, price (VND), link, brand reputation level
- Why it fits the user's specific need
- Delivery speed, seller location

### Phase 3: Refine

- When user narrows criteria (e.g., "sling only", "wrap only"), re-search with refined terms
- Rank by brand reputation + reviews, not just price
- Provide direct clickable purchase links

## Credible-source research phase (global, pre-local)

Use when the task asks for "best X under $Y" citing named credible sources (Wirecutter,
Rtings, SoundGuys, Crinacle, Head-Fi, The Master Switch, etc.) — run this BEFORE the
local-market phase (or instead of it, if no local check is requested).

### Verify "recommended", not just "popular"
- For EVERY candidate model, require a concrete verdict (quote or paraphrase) from ≥1
  named credible source. Community buzz (Reddit/Head-Fi hype) is NOT a recommendation.
- Record explicit REJECTIONS too: a source that tested a hyped model and dismissed it is
  gold — e.g. Wirecutter's 2026 wired-earbuds update rejected Moondrop Chu II, 7Hz x
  Crinacle Zero:2, and Tripowin x OdiBi Vivace, all of which are community legends.
- Check the source's "last updated" date before citing (The Master Switch's IEM guide
  says "2024" but was last updated 2023 and is TWS-focused; Crinacle's ranking list is
  the "Big Reset 2023" and lacks most 2024-25 budget models).
- Rank by number of independent credible sources agreeing + price fit. Present each pick
  with source link + quote/paraphrase so the user can verify.

### Getting to the sources when the search backend is down
web_search/web_extract (Firecrawl) may return payment/quota errors. Do NOT stop — this
direct-access ladder works regardless of backend availability:
1. `browser_navigate` straight to known guide URLs (Wirecutter/Rtings/SoundGuys guides).
   Slugs change: if 404, use the site's own search box or sitemap (step 3).
2. `curl -sL <url>` for static HTML (always `-L` to follow redirects). Works for most
   non-JS sites; save to a workspace-relative file (git-bash /tmp may not map).
3. Sitemap discovery: fetch `/sitemap_index.xml` or `/sitemap.xml`, grep `<loc>` URLs
   for topic keywords (e.g. `iem|wired|earbud`) to find article slugs.
4. WordPress REST search: `/wp-json/wp/v2/search/?search=...` (trailing slash after
   /search/ is REQUIRED — plain /search 308s). Many sites disable it (404) — skip fast.
5. Search-engine HTML endpoints (duckduckgo html/lite) are usually CAPTCHA-walled in
   automated browsers; Bing occasionally returns unrelated junk. Don't burn time —
   go direct to the source's own site instead.
6. JS-rendered pages (Wirecutter, Rtings, SoundGuys search): navigate, then extract via
   `browser_console` DOM queries — e.g. section text:
   `[...document.querySelectorAll('h2')].filter(h => /Budget|Wired/.test(h.innerText)).map(...)`
   or search-result lists: `Array.from(document.querySelectorAll('#b_results > li')).map(...)`.
   Wirecutter full-article text: browser_snapshot(full=true) saves to a cache file;
   `read_file` it, then `grep`/python-parse the saved snapshot.
7. Big tables / ranking lists: save HTML via curl, strip tags in Python, regex-parse the
   structured rows (worked example: Crinacle rows `|grade|stars|model|price|signature|note|...|`
   — see references/wired-iem-under-50-2025-2026.md).
8. Wirecutter (verified Aug 2026): web_extract returns "Website Not Supported" and r.jina.ai
   returns 403, but DIRECT curl to the nytimes.com URL returns HTTP 200 with server-rendered
   HTML — `curl -sL -A '<browser UA>' https://www.nytimes.com/wirecutter/reviews/best-smartwatches/ -o page.html`,
   then strip `<script>/<style>/<tags>` in Python + squeeze whitespace → full article text
   incl. prices/verdicts. Works for any nytimes.com/wirecutter/reviews/ page (tested with the
   smartwatches guide, updated Nov 2025).
9. Blocked-review-page fallback: web_search result descriptions frequently carry the review's
   actual verdict sentence (e.g. PCMag Xiaomi Watch S4 snippet: "...you cannot interact with
   them. It only allows you to dismiss..."). Treat it as a citable quote attributed to that
   URL when the page itself won't scrape — the snippet IS the source's own text.

### Amazon.fr / Amazon EU direct extraction (verified Aug 2026)
For "verify an actual listing exists with price + rating" tasks on Amazon.fr (also applies to
.de/.co.uk): 
1. curl gets HTTP 202 + empty body (bot wall) — do NOT retry hard; go to the browser.
2. `browser_navigate` to `https://www.amazon.fr/s?k=<query>` works (serves EN via `/-/en/`).
   A cookies dialog may appear → click "Decline" once. Search page is server-rendered HTML.
   **Pitfall: the returned snapshot may be `(empty page)` with element_count 0 even though the
   page rendered fully** (bot-wall hits the AX tree, not the DOM). Do NOT conclude failure —
   verify via `browser_console`: `({title: document.title, results: document.querySelectorAll('div[data-component-type="s-search-result"]').length})`, then extract (step 3).
3. Search-result DOM extraction via `browser_console` — selectors that actually work:
   - Full title: `.a-color-base.a-text-normal` (NOT `h2 span` — that returns only the brand)
   - Price: `.a-price .a-offscreen`; Rating: `.a-icon-alt`
   - Review count: `span[aria-label*="évaluations"]` aria-label, or `.s-underline-text`
   - URL: `a[href*="/dp/"]` → normalize to `https://www.amazon.fr/dp/<ASIN>`
   - Sponsored ads: `.puis-sponsored-label-text` (filter them out)
4. Batch N searches in ONE browser_console call via same-origin `fetch(url)` + `DOMParser`
   (Amazon serves full server-rendered search HTML to fetch). Max ~3 queries per call and NO
   artificial `setTimeout` sleeps between fetches — sleeps push the eval over its timeout
   ("3 queries + 2s sleeps" timed out; "3 queries, no sleeps" succeeded). Slice to ~8
   results/query; each fetch+parse ≈ 1.3–3s. Full working snippet in
   `references/amazon-fr-french-baby-brands.md`.
5. If the browser backend dies (CDP 502 / auto-launch failure), fall back to the jina
   reader: `curl https://r.jina.ai/<full-amazon-url>` (or `urllib` in execute_code) —
   returns markdown for BOTH search and product pages. Product entries parse as
   `## [Title](url)` headings (url contains /dp/ASIN) followed by price/rating lines
   (`€X`, `N out of 5 stars`, `(N)`). Product pages via jina give the exact variant title
   (e.g. "Sleeveless Sleeping Bag … 0-6 Months") — great for size confirmation. Caveat:
   jina rate-limits after ~5–8 consecutive searches (pages return empty, parse to []) —
   pause or switch back to the browser; product-page fetches are more forgiving than searches.
6. git-bash `/tmp` does not persist between terminal calls on this Windows host — save
   fetched pages to workspace paths (`~/file.txt`), not /tmp.
7. Clothing gotchas: search-page price is for ONE size variant (often the preemie/smallest)
   — record as "from €X" and note variant prices differ; FR baby-clothing listings often
   have tiny review counts (1–70) — normal for the category, don't filter them out; some
   brand listings are old-season 3P stock (titles carry model codes like "A0faz") — real
   listings, but flag the vintage.

### Credible-source cheat sheet (consumer audio, verified Aug 2026)
- Wirecutter wired-earbuds guide: nytimes.com/wirecutter/reviews/the-best-200-in-ear-headphones/
  (old slug /reviews/best-wired-earbuds/ 404s). Under-$50 verdicts there: Moondrop Quarks
  (~$15, best sub-$20), Sony IER-EX15C USB-C (~$20-25); its budget pick is Tin HiFi T3 Plus (~$59).
- Crinacle IEM ranking: crinacle.com/rankings/iems/ (parseable table; S→F grades + value stars).
- Rtings wired roundups are over-ear-focused; weak source for sub-$50 wired IEMs specifically.
- SoundGuys wired listicles' old slugs 404; site search is JS-rendered; thin wired-IEM coverage.

## Vietnamese e-commerce quirks

| Platform | Automated access | Notes |
|---|---|---|
| **Tiki.vn** | ✅ Via browser tools | Returns clean product listings with prices, ratings, sold counts |
| **Lazada.vn** | ✅ Via browser tools | Good search results, works with `browser_navigate` + browser_console for URL extraction |
| **Shopee.vn** | ⚠️ Prices login-walled; URLs harvestable | Search/API/product pages all return login wall (error 90309999). Workaround: harvest product URLs via Bing RSS (`site:shopee.vn <model>` + `format=rss`), verify live via curl, benchmark prices from VN specialist retailers — full technique in `product-research-local` skill ("Shopee.vn harvesting"). |
| **FPT Shop / CellphoneS / Hoàng Hà Mobile / TGDĐ** | ✅ Via direct urllib/curl | VN big-box chains, `chính hãng` (officially imported) stock. Pages show SALE + crossed-out list price in VND. FIRST stop for "officially sold in Vietnam?" verification + VND price anchoring (use the sale price for budget math). If web_extract/Firecrawl throws ERR_TUNNEL_CONNECTION_FAILED on TGDĐ, fetch with plain urllib/curl + desktop UA — the site is server-rendered and parses fine (don't switch sites). Per-site selectors (TGDĐ `data-name`/`data-price` cards + `&#x20AB;` entity, HoangHa embedded `insider_object.listing` JSON, CellphoneS SEO price table, FPT product-page `"price"` JSON) + EOL detection (`Ngừng kinh doanh`) are in `product-research-local` ("Official VN retail chains"). |

### How to search on Tiki
1. `browser_navigate(url="https://tiki.vn/search?q={Vietnamese search terms}")`
2. `browser_snapshot()` to see results
3. Extract product URLs via `browser_console(expression="Array.from(document.querySelectorAll('a[data-view-id*=\\"product\\"]')).map(a => ({title: a.querySelector('h3')?.innerText?.trim()?.substring(0,40), href: a.href}))")`

### How to search on Lazada
1. `browser_navigate(url="https://www.lazada.vn/catalog/?q={search terms}")`
2. `browser_snapshot()` to see results
3. Extract product URLs via `browser_console(expression="Array.from(document.querySelectorAll('a')).filter(a => a.href && a.href.includes('lazada.vn/products/')).map(a => ({text: a.innerText.trim().substring(0,60), href: a.href})).filter(x => x.text)")`

### Vietnamese search terms (baby/health)
- Baby carrier: `địu em bé`, `địu vải`, `đai địu`, `sling`
- Wrist brace: `nẹp cổ tay`, `viêm gân`, `nẹp ngón tay cái`
- Thumb spica: `đai cố định ngón tay cái`
- Nursing pillow: `gối cho con bú`
- Wrap carrier: `địu quấn`, `khăn quấn địu em bé`

## Identifying a product from its packaging (image-first search)

Use when the search term is VISUAL — "the tea with the purple cat on the box", a mascot, an
illustration, a colour scheme — and text search returns only generic roundups.

1. **Image search through Bing's async endpoint** (curl + desktop UA, no browser needed):
   ```bash
   curl -s -A "$UA" "https://www.bing.com/images/async?q=sleep+tea+box+cat&first=1&count=35&adlt=off" -o out.html
   ```
   Parse the `m="{...}"` attributes → `t` (result title), `murl` (image URL), `purl` (source page).
2. **Shape the query around products/brands, never around the visual description.** Brand/product
   queries ("pukka night time tea box", "clipper sleep easy tea box") return the genuine pack shots;
   vague descriptive queries ("sleep tea purple cat box uk") make Bing silently substitute unrelated
   stock imagery (sleep-cycle infographics, real cats). A junk result set means the QUERY is wrong —
   not that the product may not exist. Always read the returned titles before drawing a conclusion.
3. **Rendered/JS pages: drive the real browser.** `browser-control execute --file ./search.js --json`
   (relay 127.0.0.1:19989) with `page.goto(...)` then
   `page.$$eval("a.iusc", els => els.map(e => e.getAttribute("m")))` to read the same `m=` JSON.
   Two sandbox facts: `require` is NOT defined inside execute (use the injected `fs` / `path`
   aliases), and the CLI's `--json` stdout is prefixed by a
   `Session: <id>. Continue with --session <id>.` line — parse from the first `{`.
4. **Download candidates and batch-inspect as a numbered contact sheet.** `curl -sL -A "$UA" -H
   "Referer: <purl>"` each image, then a PIL montage of 25 tiles (5x5, 320px cells, `#<index>`
   drawn in each corner) so ONE vision call covers 25 images; keep an index map (tile → title/url)
   so any hit traces back to its product page. Working script: `references/visual-packaging-identification.md`.
5. **Then apply the grounding protocol below** — an ungrounded vision answer is not evidence.

### Grounding protocol for vision-model inspection
A vision model will confidently invent the exact attribute you asked about. Observed on real pack
shots: asked whether a cat appeared, it reported a purple cat on a Twinings Superblends Sleep box, a
black cat on Heath & Heather Night Time, and a purple cat on a US Aldi sleep tea — all three
disproved at full resolution and in crops.
- Ask for a **description plus a transcription of the printed brand/product wording**, not a yes/no
  on your hypothesis.
- **Discard any answer whose transcribed brand text does not match the pack actually being
  inspected** — that transcription is the grounding check which catches an invented illustration.
- A leading question ("is there a purple cat on this box?") is not evidence. Confirm at full
  resolution with crop-and-upscale (quadrants, or a tight crop of the pack region) before naming a
  product.
- Require two agreeing checks (a different crop, or the same pack re-fetched from another retailer)
  before reporting an attribute; otherwise report it as unconfirmed and say what the pack does show.

## Pitfalls
- Never report a product's visual feature (mascot, colour, illustration) from a single vision answer
  — leading questions make the model invent it. Ground every visual claim with a printed-text
  transcription that matches the pack plus a high-resolution crop re-check (see "Grounding protocol
  for vision-model inspection").
- Shopee prices/ratings/sold are login-walled — API bypasses are dead ends (error 90309999). But product URLs ARE harvestable via Bing RSS and prices can be benchmarked from VN specialist retailers; see `product-research-local` skill ("Shopee.vn harvesting" section) for the technique. Never fabricate Shopee listing prices/ratings/sold counts — mark them `n/a (app-only)`.
- E-commerce pages are JS-rendered SPAs; curl alone won't extract product data
- Search engines (Google, Bing, DuckDuckGo html/lite) are routinely CAPTCHA-walled or return junk in automated browsers — don't build a workflow on them. Discover URLs via the source site's own sitemap, known guide slugs, or direct navigation (see credible-source section)
- If web_search/web_extract returns a payment/quota error, use the direct-access fallback ladder in the credible-source section instead of stopping — it works regardless of backend availability
- web_search and web_extract share a Firecrawl rate limit (~11 req/min; error: "Rate Limit Exceeded... resets at <time>"). Pace batches to ≤4-5 calls/round and interleave extracts; the window resets within ~60s — re-issue the batch after the reset timestamp instead of stopping or shrinking scope
- Many international brands (Moby wrap, Baby K'tan, Solly Baby) are NOT available on Vietnamese platforms
- When comparative shopping, Lazada's search results include many irrelevant items for common terms

## Related skills
- `baby/*` skills for baby-care logging/tracking

## References
- `references/wired-iem-under-50-2025-2026.md` — verified Wirecutter/Crinacle verdicts for budget wired IEMs (Aug 2026), incl. rejected models + Phase 2 (Shopee/Tiki) candidate list. Worked example of the Crinacle ranking-table parse.
- `references/wearables-vn-iphone-2026.md` — verified VN availability map (official vs parallel-import: Garmin/Amazfit/Huawei/Xiaomi YES, Withings NO, Fossil dead), VND price anchors at big-box chains, per-brand iOS compatibility (notification-reply limits per brand), and credible review URLs for smart/hybrid watches — for any "watch for an iPhone user in VN" task. Aug 2026 model-level refresh (15 models, per-model VND prices, warranty terms, EOL + import-only verdicts) in `product-research-local` → `references/vn-retail-chains-smartwatch-pricing.md`.
- `references/amazon-fr-french-baby-brands.md` — verified Amazon.fr presence map for mid-premium French baby brands (which brands have listings vs direct-sell-only, key ASINs, gigoteuse/sleep-sack landscape) + the working browser-console JS and jina-reader Python snippets for Amazon.fr extraction.
- `references/french-baby-import-2026.md` — the complementary VN-side filter: 18-brand availability verdict table (RARE/ABSENT vs PARALLEL-only vs AVAILABLE, with Tiki/Lazada/Shopee evidence) + suitcase-import buying rules (size buy-up, hot-climate cotton, compact-only). Use with the amazon-fr reference for any France→VN baby import task.
- `references/visual-packaging-identification.md` — the image-first kit for "find the product with X on the packaging": Bing async image-search parse, browser-control scrape snippet (fs alias + `Session:` prefix gotchas), the PIL contact-sheet script, the vision grounding checklist, and the verified UK sleep-tea packaging catalogue (which packs show cats, which do not).
