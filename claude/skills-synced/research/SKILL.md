---
name: research
description: Produce a cited pre-planning research brief for a topic, repository, or upcoming project phase and save it to `research/YYYY-MM-DD_slug.md`. Use when the user explicitly invokes `/research`, asks to understand the landscape before planning, wants prior art before building, or needs context on tools, codebases, algorithms, and literature before starting a new phase.
argument-hint: "[topic or phase] [--mode domain|codebase|math|literature|all] [--depth standard|deep] [--then ...]"
disable-model-invocation: true
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

Support these depth levels: `standard`, `deep`.

- Default to `--depth standard`.
- Use `--depth deep` when the topic is technically dense, evidence quality is central, or the user explicitly asks for extra rigor.
- `standard` should stay compact and high-signal.
- `deep` should widen search, compare competing approaches more explicitly, and gather enough evidence to surface contradictions and caveats without turning into a paper.

## Research Workflow

For each selected mode, run this sequence in order:

1. `Discovery` - identify the most relevant sources, repos, docs, papers, or reports for that mode.
2. `Verification` - confirm the key claims you plan to use, note source quality, and reject or flag unverified material.
3. `Comparison` - compare the strongest approaches, implementations, or findings rather than listing sources independently.
4. `Synthesis` - write the mode section with reusable conclusions, missing pieces, contradictions, and planning implications.

Then write the cross-mode synthesis after all selected modes complete.

## Core Operating Rules

- Inspect local repository context first when the workspace is relevant.
- Prefer official docs, maintained repos, technical reports, standards bodies, and open papers over commentary.
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

## Subagent Policy

- Default to no subagents for single-mode or narrow topics.
- Use one focused subagent when a single selected mode is clearly large enough to benefit from isolated exploration, such as a large codebase survey or literature-heavy scan.
- Use at most two focused subagents unless `--mode all` or equivalent scope makes broader parallelization clearly worthwhile.
- Assign one mode or one tightly scoped evidence-gathering task per subagent.
- The main agent must merge, deduplicate, and reconcile all findings before writing the brief.

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
**Depth:** <standard|deep>
**Invocation context:** <original request>

---

## Synthesis
<2-4 short paragraphs>

<mode sections in execution order>

## Sources
- [Title](URL) - source type; why it matters
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

## Deterministic Path Helper

- Use the bundled `next_research_path.py` helper when its installed path is known in the current environment and a shell call is simpler than manual slugging.
- If the helper path is not readily available, derive the output path manually using the same filename rules in this skill.
- Pass the raw topic string exactly once and use the returned path as the save target.

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
