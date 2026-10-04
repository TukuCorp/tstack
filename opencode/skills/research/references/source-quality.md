# Source Quality Rules

Use these rules to keep research briefs high signal.

## Preferred Source Order

1. Official documentation and source repositories
2. Technical reports from labs, institutes, standards bodies, and major operators
3. Peer-reviewed papers and credible preprints
4. Maintained practitioner write-ups with concrete evidence
5. Aggregators only when they point to stronger primary sources

## Citation Discipline

- Link every material claim to a URL near the claim it supports.
- Keep URLs canonical when possible.
- Note paywalled, dead, redirected, or rate-limited sources explicitly.
- Distinguish observed facts from inference.
- For disputed claims, use narrow paraphrase or direct quotation and cite immediately.
- Keep a final `## Sources` section, but do not rely on it as the only citation mechanism.

## Verification Rules

- Prefer primary sources over summaries whenever the claim matters.
- Treat unverified or weakly sourced claims as excluded or explicitly flagged, not quietly accepted.
- Verify current status for repos, APIs, standards, and product claims before repeating them.
- When multiple strong sources conflict, report the conflict instead of picking a side silently.

## Codebase Quality Signals

- Default branch activity within the last year
- Clear README or docs
- Evidence of releases, issues, or maintainer responsiveness
- Observable architecture or API surface that matches the documented claims
- Stars or adoption signals as a weak secondary factor, not the main one

## Literature Quality Signals

- Recency
- Credible venue or institution
- Clear abstract or methods section
- Open access when possible
- Relevance to the exact formulation rather than a neighboring problem
- Comparable setting, dataset, or assumptions when making cross-paper claims

## Anti-Patterns To Avoid

- `Vibe citing` - mixing several real sources into one unsupported claim or citation.
- `Cherry-picking` - selecting only evidence that supports the preferred plan.
- `Source tier inflation` - treating blogs, marketing pages, or weak gray literature like peer-reviewed evidence.
- `Comparison by slogan` - saying one option is "better" without criteria, evidence, or scope.
- `Inference drift` - presenting your synthesis or guess as if the source stated it directly.

## Sparse-Evidence Rule

- Prefer a short honest section over padded speculation.
- Say when no strong source was found.
- Flag missing reference implementations or contradictory evidence plainly.
- Lower confidence when evidence is indirect, sparse, stale, or inconsistent.

## Synthesis Rules

- State what should be reused.
- State what appears missing.
- State what changes the expected implementation or planning path.
- Use `[NOTE]` for assumption-changing findings.
- Label meaningful inference as inference when it goes beyond the literal source text.

## Scale Tiering and Ratio Enforcement (exhaustive depth)

Applies only under `--depth exhaustive` (see `exhaustive.md`).

- Map every candidate to a tier using the Preferred Source Order above: tier 1 = official docs /
  source repos; tier 2 = lab/institute/standards/operator reports; tier 3 = peer-reviewed papers and
  credible preprints; tier 4 = practitioner write-ups; tier 5 = aggregators / marketing.
- `qualified = tier <= 3`. Enforce per-bucket ratios on the qualified set only - never fill a quota
  with tier 4-5 material to hit a number.
- The high-volume wide pass raises tier-inflation risk: the industry bucket especially attracts vendor
  marketing dressed as research. Tag it tier 4-5, not tier 2.
- When qualified sources fall short of a bucket target, either reallocate to a surplus bucket (default)
  or, under `--strict-ratio`, report the shortfall and lower that bucket's confidence.
