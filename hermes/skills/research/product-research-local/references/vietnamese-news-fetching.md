# Vietnamese News Fetching — Reliable Sources & Techniques

Verified Aug 2026 while building the daily VN news brief (live script:
`~/AppData/Local/hermes/scripts/vn-weekly-news.py`). These techniques give
**real, clickable article URLs** with **reliable pubDates** — the two things
that made earlier versions of the brief useless (Google News redirect links
and no freshness filter).

## Core rule: real article URLs, never redirect wrappers

- **Google News RSS** (`news.google.com/rss/search?q=...&hl=vi&gl=VN`) returns
  good Vietnamese results, but EVERY link is a protobuf-encoded redirect
  (`news.google.com/rss/articles/CBMi...`). The payload format changes
  repeatedly; base64 decoding is unreliable; fetching the page's og:url
  returns the SPA shell. Do NOT build a pipeline on it.
- **Bing News RSS is the reliable real-URL source:**

  ```
  https://www.bing.com/news/search?q=<urlencoded>&format=rss&setlang=vi
  ```

  Links look like `bing.com/news/apiclick.aspx?ref=FexRss&...&url=<urlencoded real article>`.
  Extract the real URL with:

  ```python
  m = re.search(r'[?&]url=([^&]+)', link)
  real = urllib.parse.unquote(m.group(1)) if m else link
  ```

  pubDate parses with standard RFC822 formats (`%a, %d %b %Y %H:%M:%S %Z` /
  `%z`). Works from this machine without API keys. Note: plain Bing web search
  (`bing.com/search?q=...&format=rss`) returns junk pages, NOT news — use the
  `/news/search` endpoint.

## Direct feeds (no search middleman)

- **CafeBiz**: `https://cafebiz.vn/rss/home.rss` — 60+ fresh items with real
  cafebiz.vn URLs. pubDate format: `Tue, 04 Aug 2026 00:02:00 +07`.
  ⚠️ Python `%z` requires `+0700`; the 2-digit `+07` fails silently and the
  item gets dropped. Normalize first:

  ```python
  s = re.sub(r'([+-]\d{2})$', r'\1:00', pd)   # +07 -> +07:00
  dt = datetime.strptime(s, "%a, %d %b %Y %H:%M:%S %z").replace(tzinfo=None)
  ```

- **Znews (Tri thức online)**: no public RSS. Scrape the homepage `https://znews.vn/`:
  - Response body is gzip-compressed even when you don't ask — send
    `Accept-Encoding: gzip, deflate` and `gzip.decompress(body)` (fallback
    `zlib.decompress`), then decode utf-8.
  - Article URL shape: `https://znews.vn/<slug>-post<id>.html`
  - Title lives in `<h3 class="article-title"><a href="...">Title</a></h3>`
    (anchor text; strip inner tags, collapse whitespace).
  - Date lives near the block: `<span class="date">3/8/2026</span>` (dd/mm/yyyy).
  - Category pages (`https://znews.vn/kinh-doanh-tai-chinh.html`) must be
    filtered out — they match `/^[a-z0-9-]+\.html$/` with no `-post<id>`.

## Political/geopolitics outlets (verified Aug 2026)

- **BBC Tiếng Việt — RSS**: `https://feeds.bbci.co.uk/vietnamese/rss.xml`.
  The bare `bbc.com/vietnamese` page is connection-refused from this machine;
  always use the `feeds.bbci.co.uk` RSS endpoint. URLs come with an
  `?at_medium=RSS&at_campaign=rss` suffix — harmless, keep or strip.
- **Fulcrum (ISEAS) — RSS by tag**: `https://fulcrum.sg/tag/vietnam/feed/`
  (also `/feed/` for all). Slow cadence (~1-2/week on the tag) → use a wider
  freshness window (max_days=21+) or the section comes back empty.
- **The Diplomat — NO direct access**: thediplomat.com refuses connections.
  Fetch via Bing News RSS `site:thediplomat.com Vietnam` — returns real
  thediplomat.com URLs with parseable pubDates. Needs max_days=21.

## Bing News RSS rate limit (critical ordering pitfall)

Bing News RSS returns **empty** after several rapid sequential queries. In a
multi-section script, if the biz section (5 company queries × up to 2
attempts) runs before a later Bing-dependent source (e.g. The Diplomat), that
source silently returns 0 items even though it works standalone. Symptoms:
source section missing while its direct RSS siblings render fine.

Fix (use both):
1. **Fetch Bing-dependent sources FIRST** in the script, before the batch of
  company queries burns the quota. Cache results, render later.
2. **Retry with backoff**: 3 attempts, `time.sleep(2 * (attempt + 1))` between.

Diagnose by fetching the source standalone (works) vs inside the full script
(0 items) — the difference is call order, not the source.

## Multi-source allocation (avoid one feed hogging the brief)

When mixing sources, round-robin with **per-source budgets** so a dominant
feed can't fill every slot before the others run. For N total items across 2
sources: first source gets `ceil(N/2)`, second `floor(N/2)`; shuffle source
order per run for variety. Label each item with its source so the reader can
tell them apart.

## Dedup & freshness pattern (used in the daily brief)

- State file `~/.hermes/vn-news-state.json`: `{"seen": {"YYYY-MM-DD": [urls]}}`,
  rolling 7-day window (prune keys older than cutoff on each load).
- `is_seen` must check membership in ANY day's url list — `if key in seen`
  where `seen` is the day→urls dict checks dict KEYS (dates), silently
  disabling dedup. Iterate the lists.
- Filter items to ≤14 days via pubDate before adding; sort newest-first.
- Fallback: if nothing fresh, show the top items even if seen — a brief that
  renders empty is worse than one that repeats. Real URL is the dedup key
  (stable across days; titles/descriptions vary).
