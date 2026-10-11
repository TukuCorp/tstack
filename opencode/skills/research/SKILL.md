---
name: research
description: Produce a cited pre-planning research brief for a topic, repository, or upcoming project phase and save it to `research/YYYY-MM-DD_slug.md`. Use when the user explicitly invokes `/research`, asks to understand the landscape before planning, wants prior art before building, or needs context on tools, codebases, algorithms, and literature before starting a new phase.
argument-hint: "[topic or phase] [--mode domain|codebase|math|literature|all] [--depth standard|deep|exhaustive] [--sources N] [--ratio github=..,academia=..,industry=..,web=..] [--strict-ratio] [--max-workers K] [--then ...]"
allowed-tools:
  - Bash
  - Read
  - Write
  - Glob
  - Grep
  - WebFetch
  - Task
  - context7_resolve-library-id
  - context7_query-docs
---

# Research

## Purpose

Produce a compact, source-backed brief before planning or implementation.
Ground the next phase in existing tools, repos, methods, and published work rather than assumptions.

This skill is for research briefs, not paper drafting.
Do not produce APA-style report sections, journal prose, or paper-writing scaffolding.

## Trigger

- Run only on explicit `/research`.
- Treat `$ARGUMENTS` as the research topic plus optional flags.
- Do not auto-trigger during normal implementation, coding, or casual discussion.

## Output Contract

- Save one markdown brief to `research/YYYY-MM-DD_slug.md` in the current workspace.
- Create `research/` if it does not exist.
- Derive a 2-4 word ASCII kebab-case noun-phrase slug from the topic.
- If a same-day filename already exists, append `-2`, `-3`, and so on.
- Print the saved filepath after writing the brief.
- Under `--depth exhaustive`, also save the source ledger to `research/sources/YYYY-MM-DD_slug.sources.jsonl` (create `research/sources/` if needed) and print its path alongside the brief.

## Mode Selection

Support these modes: `domain`, `codebase`, `math`, `literature`, `all`.

- If `--mode all` is present, run `domain -> codebase -> math -> literature`.
- If one or more `--then` flags are present, preserve the explicit order.
- If no mode is given:
  - Run `domain -> codebase` when the topic names a repo, package, API, or active workspace.
  - Run `domain -> math -> literature` when the topic is algorithmic, optimization-heavy, or formulation-heavy.
  - Run `domain -> codebase -> math -> literature` when the topic is both implementation-centered and formulation-heavy.
  - Run `domain -> literature` otherwise.
- Add `codebase` whenever a specific repository or package is central to the question.
- Run modes sequentially so later modes can build on earlier findings.
- Treat `--then` as an explicit ordered mode list extension; ignore duplicates after their first appearance.

## Depth Selection

Support these depth levels: `standard`, `deep`, `exhaustive`.

- Default to `--depth exhaustive`.
- Use `--depth deep` when the topic is technically dense, evidence quality is central, or the user explicitly asks for extra rigor but wants fewer sources than exhaustive.
- Use `--depth standard` for quick, compact research briefs with 3-8 strong sources. Useful when the user wants a lightweight overview with minimal overhead.
- Guard: `--depth exhaustive` is resource-intensive (runs 250+ source wide-pass with orchestrator fan-out). For simple or quick questions, suggest `--depth standard` or `--depth deep` instead.
- `standard` should stay compact and high-signal.
- `deep` should widen search, compare competing approaches more explicitly, and gather enough evidence to surface contradictions and caveats without turning into a paper.
- `exhaustive` switches on the source-bucket ratio system, orchestrator-worker fan-out, two-pass retrieval, and source ledger in [references/exhaustive.md](references/exhaustive.md). The written brief still stays compact; the volume lives in the ledger.

## Exhaustive Depth

These flags apply only under `--depth exhaustive` (ignore them at other depths, with a one-line notice):

- `--sources N` - total wide-pass source target. Default `250`. Clamp to `[50, 400]`; below 50, tell the user to use `--depth deep` instead.
- `--ratio github=..,academia=..,industry=..,web=..` - relative bucket weights, normalized to sum 1. Omitted buckets are excluded; unknown keys are an error. Per-bucket target = `round(N * weight)`, remainder to the largest bucket.
- `--strict-ratio` - forbid cross-bucket reallocation when a bucket cannot meet its target with qualified sources.
- `--max-workers K` - cap concurrent research subagents. Default `5`.

Default ratio is an even 4-way split (`github=0.25, academia=0.25, industry=0.25, web=0.25`). If `--ratio` is omitted, **ask the user to confirm or adjust this ratio before running the wide pass** (all four buckets are script-filled and quota-free when `FIRECRAWL_API_KEY` is set; if Firecrawl is unavailable, `industry`/`web` fall back to `WebFetch` against authoritative domains and shortfalls backfill into `github`/`academia` at high `--sources`); if `--ratio` is passed explicitly, use it without asking. Then print the final ratio used. Follow [references/exhaustive.md](references/exhaustive.md) for bucket backends, the mandatory Wide-Pass Execution discipline, the ask-before-running step, saturation rules, the tier-based quality gate (`qualified = tier <= 3`), and the source ledger.

## Background Execution

Run the research in the background so the user can keep working while it reads.

- Finish every interactive step first (subject check, the exhaustive ratio confirmation),
  then launch the work in the background and tell the user it is running.
- `standard` / `deep`: launch one background subagent that runs the full workflow and
  writes the brief. Give it the topic, flags, modes, output path, and these rules.
- `exhaustive`: the lead stays in the main session; launch the bucket workers as
  background subagents and merge, tier, and write when they report back.
- Do not predict or summarize findings before the run reports back. When it does,
  print the saved filepath(s).
- If the harness has no background subagents, run in the foreground as before.

## Research Workflow

For each selected mode, run this sequence in order:

1. `Discovery` - identify the most relevant sources, repos, docs, papers, or reports for that mode.
2. `Verification` - confirm the key claims you plan to use, trace each back to the source that owns it, note source quality, and reject or flag unverified material.
3. `Comparison` - compare the strongest approaches, implementations, or findings rather than listing sources independently.
4. `Synthesis` - write the mode section with reusable conclusions, missing pieces, contradictions, and planning implications.

Then write the cross-mode synthesis after all selected modes complete.

## Core Operating Rules

- Inspect local repository context first when the workspace is relevant.
- Prefer official docs, maintained repos, technical reports, standards bodies, and open papers over commentary.
- Follow every material claim back to the source that owns it (the official doc, spec,
  source code, first-party API, or original paper) and cite that; when a secondary
  write-up is all you can find, cite it as secondary and say the primary was not located.
- Every material claim must carry a nearby citation, not only a trailing source list.
- Distinguish observed fact from inference explicitly.
- Surface contradictions, uncertainty, and sparse evidence plainly.
- Reject or flag claims that cannot be verified well enough to rely on.
- Keep the brief compact even in `deep` mode; increase rigor, not verbosity for its own sake.

## Tool and Source Strategy

- Use local repo tools first for codebase context: `Glob`, `Grep`, `Read`, and git metadata when relevant.
- Use `gh` or GitHub API for repository discovery, README retrieval, file trees, maintenance signals, issues, releases, and commit recency.
- Use `WebFetch` for direct URLs, DeepWiki pages, arXiv abstracts, official docs, and publication portals.
- Use Context7 when the topic centers on a known framework or package and up-to-date library docs matter.
- Prefer source-native search pages and direct URLs over generic result-page scraping.
- Under `--depth exhaustive`, all four buckets are filled by the script-driven helper at `scripts/wide_pass.py`, including `industry`/`web` via Firecrawl search (requires `FIRECRAWL_API_KEY`); when Firecrawl is unavailable, `industry`/`web` fall back to `WebFetch` against topic-derived authoritative domains (no general web search tool in this environment). See [references/exhaustive.md](references/exhaustive.md) for the full backend assignment.

## Subagent Policy

- Default to no subagents for single-mode or narrow topics.
- Use one focused subagent when a single selected mode is clearly large enough to benefit from isolated exploration, such as a large codebase survey or literature-heavy scan.
- Use at most two focused subagents unless `--mode all` or equivalent scope makes broader parallelization clearly worthwhile.
- Assign one mode or one tightly scoped evidence-gathering task per subagent.
- The main agent must merge, deduplicate, and reconcile all findings before writing the brief.
- Exception: under `--depth exhaustive`, use the orchestrator-worker fan-out in [references/exhaustive.md](references/exhaustive.md) instead - one worker per active source bucket (split a bucket into two when its target exceeds 50), capped by `--max-workers` (default 5). The lead still merges, dedupes, tiers, and writes the brief.

## Mode Guides

For detailed query patterns, evidence standards, and section templates, see:
- [references/modes.md](references/modes.md)
- [references/source-quality.md](references/source-quality.md)
- [references/examples.md](references/examples.md)

### Domain

Identify the landscape, leading tools, dominant approaches, prior art, and known gaps.

### Codebase

Identify relevant repositories, architecture patterns, important files, maintenance signals, DeepWiki coverage, and reuse opportunities.

### Math

Identify formulations, algorithms, assumptions, complexity, solver choices, approximations, failure modes, and reference implementations.

### Literature

Identify recent papers, technical reports, credible practitioner write-ups, evidence quality, contradictions, and gaps in published work.

## Brief Structure

Use this exact top-level structure:

```markdown
# Research Brief: <title>

**Date:** YYYY-MM-DD
**Modes run:** <comma-separated modes>
**Depth:** <standard|deep|exhaustive>
**Invocation context:** <original request>
<exhaustive only> **Sources (wide/deep):** <gathered>/<cited> | **Ratio used:** github=..,academia=..,industry=..,web=..

---

## Synthesis
<2-4 short paragraphs>

<exhaustive only: a Source Coverage table here - columns: bucket | target | gathered | qualified | cited | reallocated>

<mode sections in execution order>

## Sources
- [Title](URL) - source type; why it matters
<exhaustive only: end with a pointer to the full ledger at research/sources/<slug>.sources.jsonl>
```

## Mode Section Contract

Each mode section should use this structure:

```markdown
## <Mode Title>
### Discovery
### Verification
### Comparison
### Synthesis
### Confidence
```

Guidance:

- `Discovery` names the strongest sources or repos you found.
- `Verification` states why the evidence is trustworthy enough to use, and flags weak or missing evidence.
- `Comparison` contrasts the main approaches, implementations, or findings.
- `Synthesis` explains what should be reused, what is missing, and what changes planning.
- `Confidence` ends with `High`, `Medium`, or `Low` and one short reason.

## Citation Rules

- Put citations next to the claim, sentence, or bullet they support.
- Use canonical URLs when possible.
- For disputed or easy-to-distort claims, quote or paraphrase narrowly and cite the source immediately.
- Note paywalled, dead, redirected, ambiguous, or rate-limited sources explicitly.
- Keep the final `## Sources` section, but do not rely on it as a substitute for claim-level sourcing.

## Synthesis Rules

- Write synthesis last.
- Combine findings across modes instead of repeating section bullets.
- State what already exists, what can be reused, what is missing, and what should shape planning.
- Prefix meaningful assumption changes with `[NOTE]`.
- Distinguish evidence-backed conclusions from informed inference.
- Keep synthesis to 2-4 short paragraphs.

## Quality Bar

- Prefer 3-8 strong sources in `standard` mode and enough strong sources in `deep` mode to support useful comparison.
- State when evidence is sparse, stale, contradictory, or indirect.
- Do not invent citations, metrics, repo activity, or literature consensus.
- Do not pad thin sections.
- Prefer a short honest brief over a long speculative one.

## Completion Checklist

- Ensure the selected modes match the topic or explicit flags.
- Ensure every material claim is sourced near the claim.
- Ensure every mode section includes discovery, verification, comparison, synthesis, and confidence.
- Ensure contradictions or missing evidence are surfaced when present.
- Ensure the brief is saved under `research/` with the required filename format.
- Ensure the synthesis reflects cross-mode findings rather than section repetition.
- Ensure the saved filepath is printed at the end.

## Examples

- `/research battery storage dispatch modeling`
- `/research REopt BESS dispatch --mode codebase --then math --then literature --depth deep`
- `/research build a lightweight PR review assistant --mode all`
- `/research grid-scale battery dispatch optimization --depth exhaustive --sources 250 --ratio github=30,academia=30,industry=20,web=20`
- `/research feature store architectures --mode all --depth exhaustive`
