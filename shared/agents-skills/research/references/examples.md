# Research Examples

Use these examples to calibrate invocation, mode choice, depth choice, and selective subagent use.
Without a `--depth` flag the default is `exhaustive` (Examples 1 and 2).

## Example 1

Input:

```text
/research how REopt handles BESS dispatch
```

Expected mode choice:

- `domain -> codebase -> math -> literature`
- `--depth exhaustive` (default; no depth flag given)

Expected emphasis:

- Battery dispatch framing
- REopt repository or docs
- Optimization formulation and solver choice
- NREL or related reports and papers

Expected behavior:

- No `--depth` flag, so the default `exhaustive` applies: confirm the even default ratio with the
  user, run the helper wide pass into the ledger, and cite only the ~30-50 source deep set.
- Keep the brief compact; the volume lives in the ledger.
- Cite claims near the relevant bullets or sentences.
- Compare the formulation found in docs or code with the formulation described in papers.

## Example 2

Input:

```text
/research build a lightweight PR review assistant
```

Expected mode choice:

- `domain -> literature`
- `--depth exhaustive` (default; no depth flag given)

Expected emphasis:

- Existing review-assistant products and workflows
- Common architectural patterns
- Evidence on review quality, automation, or developer productivity

Expected behavior:

- No `--depth` flag, so the default `exhaustive` applies: confirm the even default ratio with the
  user, run the helper wide pass into the ledger, and cite only the ~30-50 source deep set.
- Surface what exists already and what remains missing.
- Avoid turning the output into a product spec.

## Example 3

Input:

```text
/research pandas dataframe validation libraries --mode codebase --then literature --depth deep
```

Expected mode choice:

- `codebase -> literature`
- `--depth deep`

Expected emphasis:

- Maintained validation libraries
- Comparison of APIs, architecture, and extension patterns
- Published guidance or ecosystem consensus
- Contradictions between documentation claims and practical limitations

Expected behavior:

- One focused subagent may be used for codebase scanning or literature gathering, but the main agent should merge results.
- The final brief should compare the strongest libraries instead of listing many similar ones.

## Example 4

Input:

```text
/research battery degradation surrogate models --mode math --depth deep
```

Expected mode choice:

- `math`
- `--depth deep`

Expected emphasis:

- Formulations
- Complexity and approximations
- Assumptions and failure modes
- Reference implementations
- Foundational and recent papers

Expected behavior:

- Surface when two methods target adjacent but not identical problems.
- Lower confidence if strong reference implementations are missing.

## Example 5

Input:

```text
/research open-source feature flag systems --mode all --depth deep
```

Expected mode choice:

- `domain -> codebase -> math -> literature`
- `--depth deep`

Expected emphasis:

- Ecosystem segmentation and product categories
- Reusable open-source architectures
- Evaluation or rollout decision logic when relevant
- Operational evidence, reports, and gaps in published work

Expected behavior:

- Up to two focused subagents may be used if scope warrants it.
- Each mode should still follow discovery, verification, comparison, and synthesis.
- Cross-mode synthesis should resolve overlap instead of repeating each section.

## Example 6 (exhaustive depth)

Input:

```text
/research grid-scale battery dispatch optimization --depth exhaustive --sources 250 --ratio github=30,academia=30,industry=20,web=20
```

Expected behavior:

- Compute per-bucket targets: github 75, academia 75, industry 50, web 50; print them and the final
  ratio. `--ratio` was passed, so there is no confirmation prompt.
- The lead runs `scripts/wide_pass.py` with 2-4 queries per bucket: `gh search` (github), OpenAlex
  (academia), and Firecrawl search (industry and web; needs `FIRECRAWL_API_KEY`). It appends deduped
  candidate rows to `research/sources/<date>_battery-dispatch-optimization.sources.jsonl`; re-run it
  with broader queries for any bucket still short of target.
- Fan-out is optional. The lead may hand buckets to workers within `--max-workers` (default 5), but
  source volume comes from the helper either way.
- Only if the helper reports `firecrawl: unavailable` do industry and web fall back to
  `WebFetch` against topic-derived authoritative domains; any shortfall is reallocated to github/academia unless `--strict-ratio`.
- Lead dedupes, tiers (`qualified = tier <= 3`; industry and web rows start at tier 4 and are promoted
  after review), enforces the ratio on the qualified set, and selects a ~30-50 source deep set for
  full-text fetch and claim-level citation.
- The brief stays compact: a Source Coverage table after Synthesis, claim-level citations for the deep
  set only, and a closing pointer to the full ledger.

## Example 7 (exhaustive, default ratio)

Input:

```text
/research feature store architectures --mode all --depth exhaustive
```

Expected behavior:

- No `--ratio` given, so first **ask the user** to confirm or adjust the even default
  (`github=0.25, academia=0.25, industry=0.25, web=0.25`) at the `--sources` default of 250; wait for
  the answer, then print the final ratio used.
- With Firecrawl available, the helper fills all four buckets (~62 each) and the run reaches ~250
  without reallocation. If it reports Firecrawl unavailable, industry and web fall back to
  `WebFetch` against topic-derived authoritative domains and will likely fall short at this size; the shortfall backfills into
  github/academia so the run still reaches ~250.
- Otherwise identical machinery: helper-driven wide pass, ledger, saturation stops, tier-gated ratio
  enforcement, compact brief plus coverage table and ledger pointer.
