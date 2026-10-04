---
name: gap
description: Systematic codebase-grounded gap analysis comparing current repo capabilities against a stated target (demo, product launch, milestone, feature set). Produces a severity-rated report with existing assets, effort estimates, and sprint sequencing that feeds directly into /plan.
argument-hint: "[target state or goal — what you want to ship, demo, or deliver]"
allowed-tools:
  - Bash
  - Read
  - Write
  - Glob
  - Grep
  - Agent
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
- Estimate effort in terms that feed `/plan` — number of phases, approximate complexity.
- Recommend sprint sequencing based on dependencies and impact.
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

## Report Template

Use the following structure as the output skeleton. Fill every section. Remove placeholder comments.

```markdown
# Gap Analysis: {{TARGET_TITLE}}

**Date:** {{DATE}}
**Scope:** {{SCOPE_DESCRIPTION}}
**Status:** Draft for Review

---

## Executive Summary

{{2-3 sentences: what's strong, gap magnitude, critical gap count, one-line recommendation}}

---

## Current Capabilities (What We Have)

| Capability | Status | Key Surfaces |
|---|---|---|
| {{Capability}} | {{Mature / Working / Partial / Planned / Missing}} | {{file paths}} |

---

## Target State

> {{Clear description of the desired end state}}

---

## Gap Analysis

### GAP-01: {{Gap Title}}

**Severity:** {{CRITICAL / HIGH / MEDIUM / LOW}} — {{One-line justification}}

**Current state:** {{What exists today, with specific file paths}}

**What's needed:**
- {{Specific requirement}}

**Existing assets to reuse:**
- {{File or module that can be extended, with what it already does}}

**Effort estimate:** {{Rough sizing — e.g., "1 multi-phase plan (3-4 phases)"}}

---

<!-- Repeat GAP-XX for each gap -->

## Second-Tier Gaps

| Gap | Severity | Summary | Existing Assets |
|---|---|---|---|
| {{GAP-XX}} | {{MEDIUM / LOW}} | {{One-line}} | {{What exists}} |

---

## Recommended Sprint Sequencing

| Priority | Gap | Rationale |
|---|---|---|
| Sprint 1 | {{GAP-XX}} | {{Why first}} |

---

## Risk Register

| Risk | Impact | Likelihood | Mitigation |
|---|---|---|---|
| {{Risk}} | {{What breaks}} | {{H/M/L}} | {{How to prevent}} |

---

## Suggested Next Step

{{Review this report, then invoke `/plan` for each critical gap.}}
```

### Severity Guide

| Rating | Meaning | Action |
|---|---|---|
| CRITICAL | Blocks the target entirely | Must address first |
| HIGH | Significantly degrades the target | Address in first sprint |
| MEDIUM | Limits value of the target | Address if time permits |
| LOW | Polish — target works fine without this | Backlog |

## Quality Bar

The report is complete when:
- Every gap is grounded in specific repo observations (file paths, module names)
- Severity ratings are justified, not just assigned
- Existing reusable assets are identified for every gap where they exist
- Sprint sequencing accounts for dependencies between gaps
- Another agent could take any gap and invoke `/plan` on it immediately
- The report is self-contained — no conversation context required

## Examples

- `/gap client demo showing real-time data pipeline with dashboard`
- `/gap production readiness for multi-tenant SaaS launch`
- `/gap MVP feature set for investor pitch next Thursday`
- `/gap API completeness for third-party integration partner`
- `/gap mobile app feature parity with web version`
