---
name: gap
description: Systematic codebase-grounded gap analysis comparing current repo capabilities against a stated target (demo, product launch, milestone, feature set). Produces a severity-rated report with existing assets, agent-unit effort estimates, and wave sequencing that feeds directly into /plan. This skill should be used only when the user explicitly invokes `/gap`.
argument-hint: "[target state or goal — what you want to ship, demo, or deliver]"
disable-model-invocation: true
allowed-tools:
  - Bash
  - Read
  - Write
  - Glob
  - Grep
  - Task
---

# Gap Analysis

## Purpose

Produce an actionable gap analysis report comparing the current state of any codebase against a stated target.
Write the gap analysis report only.
Do not write implementation code, edit product files, or start execution.
The output is designed to feed directly into `/plan` for implementation planning.

## Trigger

- Run only on explicit `/gap`.
- Treat `$ARGUMENTS` as the target-state description (what the user wants to achieve or ship).
- If `$ARGUMENTS` is empty, ask for the target state and stop.
- If the target is ambiguous, make reasonable assumptions and document them in the report.

## Output Contract

- Save one markdown report in the active workspace.
- Use `reports/` if it already exists.
- Otherwise use `docs/reports/` if that directory already exists.
- Otherwise create `reports/`.
- Use filename `YYYY-MM-DD-<slug>-gap-analysis.md`.
- Derive `<slug>` as a 2-5 word ASCII kebab-case noun phrase from the target.
- If the same-day filename already exists, append `-2`, `-3`, and so on.
- Print the saved filepath after writing the report.

## Analysis Principles

- Ground every gap claim in specific files, modules, or capabilities observed in the repo.
- Rate severity with actionable labels: CRITICAL (blocks the target), HIGH (significantly degrades the target), MEDIUM (limits value), LOW (polish/nice-to-have).
- For each gap, identify existing assets that can be reused or extended — never claim "build from scratch" when the repo has relevant code.
- Estimate effort in agent units that feed `/plan` — number of phases, approximate complexity, verification gates. No calendar time (days, weeks, sprints) except for named outside dependencies (vendors, CI, people).
- Recommend sequencing in waves based on dependencies and impact, and name the human checkpoints (reviews, logins, approvals, external waits) each wave needs.
- Write for another agent or engineer with zero shared context about this repo.

## Context Gathering

### 1. Understand the repo

Read the minimum necessary to assess capabilities relevant to the stated target:

- Project docs: `README*`, `CLAUDE.md`, `AGENTS.md`, `activeContext.md`, or equivalent.
- Project structure: top-level `ls`, then scan `src/`, `scripts/`, `tests/`, `data/`, `docs/` as relevant.
- Tech stack: identify from package files (`package.json`, `pyproject.toml`, `Cargo.toml`, `Gemfile`, `go.mod`, `Manifest.toml`, etc.).
- Recent momentum: `git log --oneline -15` to understand current development direction.
- Do NOT read every file. Read only what's needed to assess capabilities against the target.

### 2. Use research/ and docs/ when available

- Check whether `research/` exists. If so, list `research/**/*.md` and read the 1-3 most relevant to the target.
- Check whether `docs/` has architecture docs, API docs, or design docs relevant to the target.
- Extract findings that affect gap assessment.

### 3. Use existing plans/ if available

- Check whether `plans/` exists. If so, scan for existing plans that relate to the target.
- Note which planned work is already scoped (these are "planned" not "gaps") vs. what represents new gaps.

### 4. Assess current capabilities against the target

For each capability the target requires, determine:
- Does it exist? (fully, partially, or not at all)
- If partial, what works and what's missing?
- What existing code, modules, or patterns could be reused or extended?
- Don't speculate. If you can't find evidence of a capability, it's a gap.

## Build Procedure

1. Parse `$ARGUMENTS` into a concrete target state.
2. Derive a concise title and ASCII slug.
3. Select the output directory using the priority order in `## Output Contract`.
4. Gather the minimum repo context needed to perform the analysis.
5. Inspect `research/` and absorb the most relevant available briefs.
6. Read `assets/gap-analysis-template.md` and use it as the output skeleton.
7. Fill every section with request-specific and repo-specific details.
8. Save the final markdown report file and print its path.

## Required Report Structure

- Start from `assets/gap-analysis-template.md`.
- Keep the top-level sections and subsection names exactly.
- Fill every placeholder.
- Remove instructional placeholder comments from the final output.

### Severity Guide

| Rating | Meaning | Action |
|---|---|---|
| CRITICAL | Blocks the target entirely | Must address first |
| HIGH | Significantly degrades the target | Address in the first wave |
| MEDIUM | Limits value of the target | Address if time permits |
| LOW | Polish — target works fine without this | Backlog |

## Quality Bar

The report is complete when:
- Every gap is grounded in specific repo observations (file paths, module names)
- Severity ratings are justified, not just assigned
- Existing reusable assets are identified for every gap where they exist
- Wave sequencing accounts for dependencies between gaps and names the human checkpoints
- Another agent could take any gap and invoke `/plan` on it immediately
- The report is self-contained — no conversation context required

## Examples

- `/gap client demo showing real-time data pipeline with dashboard`
- `/gap production readiness for multi-tenant SaaS launch`
- `/gap MVP feature set for investor pitch next Thursday`
- `/gap API completeness for third-party integration partner`
- `/gap mobile app feature parity with web version`
