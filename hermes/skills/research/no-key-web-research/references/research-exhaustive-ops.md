# /research --depth exhaustive: wide-pass ops (verified 2026-08-11)

Operational lessons from a full `--depth exhaustive` run (OCW program ranking, ~1000-row ledger).
The `research` skill's own `exhaustive.md` is protected (non-agent-created); these notes live here so
future wide passes start from known behavior.

## 1. Firecrawl unavailable -> fallback order that works

`scripts/wide_pass.py` reports `firecrawl: "unavailable: no key"` when FIRECRAWL_API_KEY is unset,
and industry/web buckets come back empty. Do NOT jump straight to the 8-fetch WebFetch seed list:

1. **Try the environment's `web_search` tool first** — it can be live even with no Firecrawl key
   (verified 2026-08: 16/16 queries returned results; 318 industry+web rows appended in one pass).
   Fill industry (tier 3, report-flavored queries) and web (tier 4, aggregator/thread queries) with
   <=8 queries per bucket, appending candidates to the same ledger.
2. Only if `web_search` errors (credit/403/empty) -> WebFetch seed-list fallback (<=8 fetches/bucket).
3. If web_search is down entirely -> work this skill's chain (DDGS -> Bing -> wayback).

## 2. wide_pass.py per-run cap starves diversification

The helper stops a bucket once `round(target * 1.5)` NEW rows are added within THAT run — the first
query can fill the whole cap and later queries never execute. Observed: academia got 94/94 and
165/165 rows each from a single first query. Fix: re-run the helper with ONE query per run and a
small target (30-40) to diversify.

## 3. OpenAlex fuzzy-search noise

`openalex /works?search=` is fuzzy: education queries return heavy off-topic hits (ML/medical, e.g.
"Deep learning in agriculture"). Re-tier obviously off-topic academia rows to tier 5 by title
keyword before computing `qualified` counts, or the bucket looks far healthier than it is.

## 4. JS-heavy OCW/education sites defeat web_extract

ocw.tudelft.nl, open.edu, fullstackopen.com, edx.org, cl.cam.ac.uk, youtube returned empty content
to web_extract (JS shells). Workarounds: web_search snippets still carry title+description; curl
with a browser UA gets SSR pages; the Wayback CDX trick (this skill's Rung 3) handles the rest.

## 5. Ledger finalization recipe (one script)

1. Re-tier off-topic rows (see #3).
2. Mark the deep set `verified` by URL-substring match with a one-line `claim`.
3. Append missing deep rows with the bucket assigned EXPLICITLY — URL-domain heuristics
   misbucket DOI rows into `industry`; DOIs belong to `academia`.
4. Rewrite the ledger, then recompute `by_bucket` / `qualified` (tier<=3 AND topic-relevant) /
   `verified` straight from the file.
5. Coverage table `gathered` must equal rows actually in the ledger (ledger-truth rule).

## 6. Never hardcode repo signals

Deep-pass repo verification: `gh api repos/<owner>/<repo> --jq '{stars, updated_at, open_issues_count}'`
(e.g. OSSU: real value 207,852 stars, updated 2026-08 — not an estimate).

## 7. Mode selection for "rank top N" briefs

domain -> literature suffices; skip codebase mode unless a repo is the subject. The source buckets
(github/academia/industry/web) still surface repos and papers even without codebase mode.

## 8. Ledger-write safety: build rows in memory BEFORE opening for write

Never `open(ledger, "w")` while building/streaming rows in the same loop. A mid-loop crash (e.g.
KeyError on a missing field) truncates the file to 0 bytes and the `with` block closes it — the
entire gathered pool is lost (hit 2026-08-12: 180 rows wiped, had to re-run every query deck).
Build all row dicts in memory first, THEN open for write. Recovery when it happens: re-run the
same query decks (dedup keeps surviving rows) and manually re-add the lost high-value rows with
`discovered_via: "re-added after ledger truncation (initial wide pass)"`; state the recovery in
the brief's coverage narrative.

## 9. web_extract full text is cached — mine the cache instead of re-fetching

`web_extract` returns head+tail windows, but full text is always saved to
`<cache>/web/<host>-<hash>.md` (the footer names the path). When a page scrapes partially or the
inline digest is too thin (e.g. VN pages whose substance is in `triệu`/`tỷ` prices and `x`-joined
mm dims), grep the cache file with fact patterns instead of re-fetching: map host -> newest file
by mtime, then `re.finditer` price/dimension/standard-number patterns and print compact context
snippets. Deep pass under `execute_code`: batch ~10 URLs per run (5-min tool timeout),
`char_limit` ~6000, print only regex fact-lines — full pages never enter context, and the cache
files remain readable on demand.

## 10. URL normalization consistency + web_extract result guards

- Strip `www.` on BOTH dedupe keys and host-based tier lookups (`domain(u).lstrip("www.")`) —
  otherwise `www.otis.com` silently misses the `otis.com` tier row and every such source is
  mis-tiered.
- OpenAlex `doi` values can arrive double-prefixed (`https://doi.org/https://doi.org/10.xxxx`);
  canonicalize with `re.match(r"https?://doi\.org/(https?://doi\.org/)?(10\.\S+)", u)` ->
  `doi.org/<doi>`.
- `web_extract` result fields can be `None` (guard with `or ""`) and result order may not align
  1:1 with the requested URLs — build a `by_url` map keyed on the returned URL instead of zipping.
