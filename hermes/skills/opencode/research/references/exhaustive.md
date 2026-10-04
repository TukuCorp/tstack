# Exhaustive Depth

This reference governs `--depth exhaustive` only. Other depths ignore everything here.

Exhaustive trades a single compact pass for a high-volume, multi-source survey: an orchestrator
spawns one worker per source bucket, each worker accumulates candidate sources into a shared ledger,
and the lead then tiers, dedupes, enforces the bucket ratio, and writes a still-compact brief whose
volume lives in the ledger rather than the prose.

Core rule: **exhaust hundreds, read dozens.** A cheap wide pass touches many sources at metadata
level; an expensive deep pass fetches full text only for the ~30-50 that get cited.

## Source Buckets

Four buckets, each with a dedicated retrieval backend:

- `github` - source repositories and reference implementations.
- `academia` - peer-reviewed papers, preprints, and technical reports.
- `industry` - lab/gov/standards/operator/consultancy reports and whitepapers.
- `web` - maintained practitioner write-ups, docs, and evidence-bearing threads.

Buckets are orthogonal to modes. Modes set topic emphasis; buckets set source-type ratio.

## Flag Resolution

1. `--sources N`: default `250`, clamp `[50, 400]`. Below 50, tell the user to use `--depth deep`.
2. `--ratio`: relative weights normalized to sum 1. Omitted buckets are excluded; unknown keys error.
   Per-bucket target = `round(N * weight)`; push the rounding remainder to the largest bucket.
3. If `--ratio` is omitted, the **default is an even 4-way split: `github=0.25, academia=0.25,
   industry=0.25, web=0.25`**. Do not auto-pick by mode. Instead, **ask the user first** (see
   "Ask Before Running" below) and use whatever they confirm. Print the final ratio used.

   **Backend note for the even default:** all four buckets are filled by quota-free scripted backends
   (`gh`, OpenAlex, and Firecrawl search via the helper - Firecrawl requires `FIRECRAWL_API_KEY` in the
   environment), so the even split is normally achievable without cross-bucket pressure. If Firecrawl
   is unavailable (no key, invalid key, or exhausted credits), `industry`/`web` fall back to `WebFetch`
   against a topic-derived seed list of authoritative domains, which is narrower than full web search -
   this environment has no general web-search tool. At large `--sources`, the fallback `industry`/`web`
   targets will usually be capped by the domain seed list (Wide-Pass Execution, <=8 fetches per bucket,
   broad domain coverage per fetch). When that happens, **reallocate the shortfall to
   `github`/`academia`** so the run still reaches `--sources` (unless `--strict-ratio` is set). The
   brief's coverage table shows the requested 25/25/25/25 alongside what each bucket actually gathered.
4. `--max-workers K`: default `5`. `--strict-ratio`: see Quality Gate below.

## Ask Before Running

Under `--depth exhaustive`, before launching the wide pass, confirm the bucket ratio with the user
unless they already passed an explicit `--ratio`:

- Present the default `github=0.25, academia=0.25, industry=0.25, web=0.25` and the chosen `--sources`.
- Note the fallback condition: if Firecrawl is unavailable, `industry`/`web` fall back to `WebFetch`
  against authoritative domains in this environment, and the shortfall backfills into
  `github`/`academia`.
- Let the user accept the default or give different weights. Wait for the answer before any backend call.
- If `--ratio` was passed on the command line, skip the prompt and use it as given.
- Re-normalize whatever the user provides to sum 1, then compute per-bucket targets.

## Orchestrator-Worker Fan-Out

```
LEAD (main agent)
  1. parse flags, compute per-bucket targets, print the plan (targets + final ratio)
  2. decompose the topic into 2-4 sub-questions
  3. spawn WORKERS - one per active bucket; split a bucket into two disjoint-query workers
     when its target > 50; total concurrent workers <= --max-workers
  4. workers run the wide pass concurrently, each appending candidate rows to the ledger
  5. LEAD reconciles: dedupe, tier, enforce ratio, select the deep set (~30-50)
  6. deep pass: full-text fetch + claim check for the deep set (inline or one VERIFY worker)
  7. LEAD writes the brief + finalizes the ledger
```

Fan-out is an **optimization, not the source of volume.** Volume comes from batch backend calls
(`curl`/`gh`/`WebFetch` return many results per call), so the lead may run the entire wide pass directly
without spawning any workers and still reach the target. Never let the run's source count depend on
whether subagents were spawned. If you do spawn workers, give each the Wide-Pass Execution recipe below.

### Worker contract (wide pass)
- Input: bucket name, target count, topic + sub-questions, this file's backend section, ledger path.
- Loop: issue 3-6 diversified **batch** queries; append a `candidate` row (metadata only, no full
  fetch) per returned item; stop when `candidates >= 1.5 * target` or saturation fires (see Saturation).
- Return to lead: count gathered, the query list, which saturation condition fired, and any
  rate-limit/backoff events.
- Workers never write the brief and never fetch full text in the wide pass.

## Wide-Pass Execution (mandatory backend discipline)

The wide pass is built from **batch backend calls that each return many items**, not per-item
WebFetch. All four buckets are executed by a committed helper script so volume does not depend on
the model improvising; only if the script reports Firecrawl unavailable does the model add the
WebFetch-bound fallback itself.

Backend assignment is fixed. A bucket must use its assigned backend; substituting a noisier
backend for a quota-free one when Firecrawl is available is the specific bug that produced a
30-row ledger.

### Step 1 - all four buckets via the helper (run this; do not hand-roll)

Run `scripts/wide_pass.py` (next to this skill, e.g.
`%LOCALAPPDATA%/hermes/skills/opencode/research/scripts/wide_pass.py`). It calls OpenAlex (academia),
`gh search` (github), and Firecrawl search (industry, web - requires `FIRECRAWL_API_KEY` in the
environment), dedupes against the existing ledger, and writes candidate rows. It is safe to call
repeatedly. Provide 2-4 diversified queries per bucket drawn from the sub-questions:

```
python <skill>/scripts/wide_pass.py \
  --ledger research/sources/<YYYY-MM-DD>_<slug>.sources.jsonl \
  --academia-target <N_academia> \
  --academia-query "<sub-question terms 1>" --academia-query "<terms 2>" \
  --github-target <N_github> \
  --github-repo-query "<terms>" --github-code-query "<terms>" \
  --industry-target <N_industry> \
  --industry-query "<terms> report filetype:pdf" --industry-query "<terms> site:*.gov" \
  --web-target <N_web> \
  --web-query "<sub-question terms 1>" --web-query "<terms 2>"
```

It prints a JSON summary (`new_rows`, `by_bucket`, `firecrawl`, `errors`). The `firecrawl` field is
`"ok"`, `"skipped"` (no industry/web targets given), or `"unavailable: <reason>"`. If a bucket is
short of target, call it again with broader/different queries - it will only add new, deduped rows.
The academia/github buckets never use WebFetch and are not subject to session search quota, so they
carry the bulk of `--sources` even when Firecrawl is unavailable.

(Manual fallback for academia/github if the script is unavailable: `curl -s
"https://api.openalex.org/works?search=<terms>&per-page=200&mailto=<contact>"` parsing
`results[]`, and `gh search repos|code ... --json ...`. Never use WebFetch for these two buckets.)

### Step 2 - fallback: industry + web via WebFetch (only when the helper reports Firecrawl unavailable)

Trigger: the Step 1 summary's `firecrawl` field starts with `"unavailable"` (missing/invalid key or
exhausted credits). When it does, these buckets use `WebFetch` against a topic-derived seed list of
authoritative URLs/domains; this environment has no general web-search tool. The seed list is
**topic-specific** - derive it from the topic itself rather than using a fixed set. Examples
(not a fixed list):

- For energy topics: `*.eia.gov`, `*.iea.org`, `*.irena.org`, `*.nrel.gov`, `*.energy.gov`,
  operator/integrator reports, ISO/RTO sites.
- For software topics: vendor docs, major foundation sites, well-known analyst write-ups.
- For biomedical topics: `*.nih.gov`, `*.who.int`, `*.nature.com`, `*.nejm.org`, trial registries.
- For policy/standards topics: `*.gov`, `*.europa.eu`, `*.oecd.org`, standards body sites.

Use `WebFetch` to pull the seed pages or known authoritative URLs and extract candidate source
links. **Wide-pass budget: <= 8 fetches per bucket (16 total per run).** Append every candidate to
the **same ledger** the helper wrote (`status:"candidate", bucket:"industry"|"web", pass:"wide"`).
If the budget is hit before target, stop and record a deficit - do not borrow fetches. Reallocate
the deficit to github/academia (re-run the helper) unless `--strict-ratio`. Use full-text
`WebFetch` only in the deep pass. State the fallback reason (the `firecrawl` field's value) in the
brief's coverage narrative so the degraded run is visible, not silent.

**Zero-row rule:** if a bucket returns 0 rows, retry its assigned backend once with broader
seed domains before recording a deficit. Never substitute WebFetch for the helper when Firecrawl
is available.

**Ledger-truth rule:** the brief's `gathered` count for each bucket must equal the number of rows
actually in the ledger for that bucket. If they disagree, the ledger wins.

## Bucket Backends

### github
- Repo discovery: `gh search repos "<terms>" --limit 100 --json fullName,description,stargazersCount,updatedAt,url,license`
- Implementation discovery: `gh search code "<terms>" --limit 50 --json repository,path,url`
- Pagination beyond 100: `gh api "/search/repositories?q=<q>&sort=updated&per_page=100&page=N"`.
  Search caps at 1000 results per query - diversify queries instead of deep-paginating one.
- Chosen-repo deep dive (deep pass): README + tree via `gh api`, then the DeepWiki page if one exists.
- Rate limit: authenticated Search API ~30 requests/min. Budget <= 8 queries/bucket; back off on 403.
- Quality signals (`source-quality.md`): default-branch activity < 1yr, releases, issue
  responsiveness, license, README/docs. Stars are a weak secondary signal.

### academia (free; the cheap path to dozens of papers)
- OpenAlex (primary, broadest):
  `curl -s "https://api.openalex.org/works?search=<terms>&per-page=200&page=N&mailto=<contact>"`
  -> JSON: title, abstract (inverted index), publication_year, cited_by_count, open_access, doi, host venue.
- arXiv (CS/physics/math preprints):
  `curl -s "http://export.arxiv.org/api/query?search_query=all:<terms>&start=0&max_results=100"`
  -> Atom XML. Be polite: ~3s between calls.
- Semantic Scholar (citation graph, TLDRs):
  `curl -s -H "x-api-key: $SEMANTIC_SCHOLAR_API_KEY" "https://api.semanticscholar.org/graph/v1/paper/search?query=<terms>&limit=100&fields=title,abstract,year,citationCount,openAccessPdf,url"`
  -> JSON. The `x-api-key` header is **optional**: if `$SEMANTIC_SCHOLAR_API_KEY` is unset, omit
  the header and throttle to ~1 request/sec (keyless rate). With a key, raise throughput accordingly.
- Crossref (optional DOI resolution): `curl -s "https://api.crossref.org/works?query=<terms>&rows=100"`.
- Quality signals: recency (bias last 3 years unless foundational), venue/citation count, OA
  availability, relevance to the exact formulation.

### industry
- Firecrawl search via the helper (`scripts/wide_pass.py --industry-target ... --industry-query
  ...`), metadata-only, <=8 queries/bucket. Keep the query list **general** and let the lead derive
  the right domains from the topic - e.g. national labs, government agencies, standards bodies,
  major operators, established consultancies, and credible trade organizations relevant to the
  field. Query patterns pass through as search terms: `"<topic>" report filetype:pdf`, `"<topic>"
  site:*.gov`, `"<topic>" site:*.org whitepaper`.
- Fallback (Firecrawl unavailable): `WebFetch` against a topic-derived seed list of authoritative
  domains - fetch the seed index page and follow links to reports/whitepapers, <=8 fetches/bucket
  (Wide-Pass Execution Step 2).
- `WebFetch` the report pages/PDFs that survive the wide pass (deep pass only, regardless of which
  backend found them).
- Quality risk: this bucket attracts tier-inflation. Vendor marketing PDFs are tier 4-5, not tier 2.
  Tag honestly per `source-quality.md`.

### web
- Firecrawl search via the helper (`scripts/wide_pass.py --web-target ... --web-query ...`),
  metadata-only, <=8 queries/bucket, for practitioner write-ups, official docs, and
  evidence-bearing forum/issue threads.
- Fallback (Firecrawl unavailable): general `WebFetch` against practitioner write-up hubs,
  official docs sites, and evidence-bearing forum/issue threads known to the lead, <=8
  fetches/bucket (Wide-Pass Execution Step 2).
- Lowest default tier; use it for coverage and to surface primary sources the other buckets
  missed, then promote those primaries into their proper bucket.

## Source Ledger

Workers cannot hold hundreds of sources in prose, so they append rows to a shared JSONL ledger
that the lead reads back.

- Path: `research/sources/YYYY-MM-DD_slug.sources.jsonl` (same date+slug as the brief). Create
  `research/sources/` if needed.
- One JSON object per line. Schema:

```json
{
  "id": "gh-014",
  "bucket": "github|academia|industry|web",
  "url": "canonical url or DOI",
  "title": "...",
  "tier": 1,
  "status": "candidate|verified|rejected",
  "pass": "wide|deep",
  "discovered_via": "the query string that found it",
  "signal": {"stars": 1200, "updated": "2026-03", "citations": 84, "oa": true},
  "claim": "what this source supports (deep pass only)",
  "note": "paywalled | dead | redirected | rate-limited | duplicate-of:gh-002"
}
```

- Dedup key: normalized URL - lowercase host, strip query/tracking params, canonicalize DOI to
  `doi.org/<doi>`, collapse arXiv abs/pdf/version variants to the base id. Mark duplicates
  `status:rejected, note:"duplicate-of:<id>"` rather than deleting them (keeps the audit trail).
- Lifecycle: wide pass writes `candidate` rows -> lead tiers + dedupes -> deep set promoted to
  `verified` with a `claim` -> promoted-but-broken sources become `rejected` with a `note`.

## Saturation

Stop a bucket's wide pass when any one fires:

- `candidate count >= 1.5 * bucket target` (oversample so the quality gate has slack), or
- novelty drops - the latest query added < 20% new rows after dedup, or
- hard cap - 8 queries issued for that bucket.

Record which condition fired in the worker's return. Saturation is what makes "exhaustive"
terminate honestly instead of padding (Sparse-Evidence Rule in `source-quality.md`).

## Quality Gate and Ratio Enforcement

1. Tier every candidate using the Preferred Source Order in `source-quality.md` (tier 1 = official
   docs / source repos ... tier 5 = aggregators / marketing).
2. `qualified = tier <= 3`. Enforce the bucket ratio on the **qualified** set, never on raw hits, so a
   quota cannot be filled with junk.
3. Shortfall handling when a bucket cannot reach its target with qualified sources:
   - default: reallocate the deficit to the bucket with the most qualified surplus, and record it
     in the coverage table's `reallocated` column.
   - `--strict-ratio`: do not reallocate; report the shortfall and lower that bucket's confidence.
4. Deep set: from the qualified pool, pick the top ~30-50 by tier + relevance, respecting each
   bucket's enforced share. Only these get full-text fetch and claim-level citation.

## Output Additions

On top of the standard brief structure:

- Header gains `Sources (wide/deep): <gathered>/<cited>` and the final ratio used.
- A **Source Coverage** table right after Synthesis:

  | bucket | target | gathered | qualified | cited | reallocated |
  |---|---|---|---|---|---|

- Narrative and claim-level citations cover only the deep set - keeping the brief readable and
  every cited claim genuinely verified.
- End the `## Sources` section with a pointer to the full ledger:
  `Full source pool: research/sources/<slug>.sources.jsonl (<row count> rows).`
- Each bucket gets a one-line confidence reflecting its shortfalls and saturation outcome.

## Failure Handling

- A down or rate-limited backend is not a run failure: the worker records the event in the ledger
  `note`, the bucket reports a shortfall, and the run completes degraded rather than aborting.
- A missing/invalid `FIRECRAWL_API_KEY` or exhausted Firecrawl credits is not a run failure: the
  helper reports `firecrawl: unavailable: <reason>` in its summary, `industry`/`web` fall back to
  `WebFetch` per Wide-Pass Execution Step 2, and the brief states the fallback reason next to the
  coverage table.
- Parallel workers are the mitigation for wall-clock cost; `--max-workers` caps concurrency to
  respect backend rate limits.
