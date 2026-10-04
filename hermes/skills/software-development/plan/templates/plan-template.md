---
title: "{{PLAN_TITLE}}"
date: "{{DATE}}"
status: "draft"
request: "{{ORIGINAL_REQUEST}}"
plan_type: "multi-phase"
research_inputs:
  - "{{RESEARCH_INPUT_PATH_OR_NONE}}"
---

# Plan: {{PLAN_TITLE}}

## Objective
{{1-3 sentences describing the desired outcome and why it matters now}}

## Context Snapshot
- **Current state:** {{What exists today}}
- **Desired state:** {{What should exist after this work}}
- **Key repo surfaces:** {{Relevant files, modules, routes, jobs, tables, services, or docs}}
- **Out of scope:** {{Explicit exclusions}}

## Environment & Conventions
<!-- Everything the executor needs that is NOT in the repo's obvious view. Verify every command against the repo (scripts blocks, CI config); never guess. -->
- **Stack:** {{Language, framework, package manager, and the pinned versions that matter (e.g. "Python 3.12, FastAPI, uv — not pip")}}
- **Setup:** {{Exact dependency-install command}}
- **Build / Run:** {{Exact build and run commands}}
- **Test:** {{Exact full-suite command}} — single test: {{exact single-test command}}
- **Conventions & traps:** {{Naming conventions, units/currency/timezone rules, lint/format expectations}}
- **Repo map:** {{5-10 line orientation of the directories and files that matter for this plan}}

## Research Inputs
<!-- INLINE the findings that shaped the plan; the source path is provenance only — the executor may not have research/. -->
- From `{{research/file.md}}`:
  - {{Finding that changes scope, sequencing, design, or risk — copied in, not referenced}}
  - {{Finding}}
- If none: `No applicable research briefs were found in research/.`

## Assumptions and Constraints
<!-- The plan ships with ZERO open questions. Every unresolved unknown becomes an ASM with a BINDING DEFAULT the executor MUST apply unless the line is edited before hand-off. -->
- **ASM-001:** {{Assumption grounded in repo context or request}}
- **ASM-002:** {{Unresolved unknown}} — **BINDING DEFAULT:** {{the default the executor applies}}
- **CON-001:** {{Constraint that limits the solution}}
- **DEC-001:** {{Known decision already fixed by the request, a brainstorm brief, or the current system}}

## Specification
<!-- CONDITIONAL: include only when real formulas or cross-phase decision logic exist; DELETE this section otherwise.
     If math is involved: write the actual formulas in notation AND annotate every symbol in plain English.
     If no math: exact numbered step-by-step decision logic. No pseudocode, no vague descriptions. -->
{{Formulas with per-symbol annotations, and/or numbered decision logic}}

## Phase Summary
| Phase | Goal | Dependencies | Primary outputs |
|---|---|---|---|
| PHASE-01 | {{Goal}} | None | {{Outputs}} |
| PHASE-02 | {{Goal}} | PHASE-01 | {{Outputs}} |
| PHASE-03 | {{Goal or delete this row if not needed}} | PHASE-02 | {{Outputs}} |

## Detailed Phases

### PHASE-01 - {{Phase Name}}
**Goal**
{{What this phase accomplishes}}

**Tasks**
- [ ] TASK-01-01: {{Atomic task another agent could execute without extra context}}
- [ ] TASK-01-02: {{Atomic task}}

**File Changes**
- `path/to/file` ({{create|modify}}): {{What specifically to add or change — and what to leave alone}}
- `path/to/other` ({{create|modify}}): {{Specific change}}

**Function Signatures**
<!-- Complete interfaces: parameter names, types, return types. Write `None — no code interfaces change in this phase.` when genuinely inapplicable. -->
- `function_name(param: Type, other: Type) -> ReturnType` — {{one-line description of what it returns}}

**Test Specs**
<!-- Literal inputs → expected outputs, edge cases spelled out — not "write tests for X". Write `None — no testable behavior changes in this phase.` when genuinely inapplicable. -->
- {{`call_or_scenario(exact input values)`}} → {{exact expected output}}
- {{Edge case}} → {{expected behavior}}

**Dependencies**
- {{Internal or external dependency, or `None`}}

**Exit Criteria**
- [ ] {{Verifiable outcome}}
- [ ] {{Verifiable outcome}}

**Phase Risks**
- **RISK-01-01:** {{Risk and mitigation}}

### PHASE-02 - {{Phase Name}}
**Goal**
{{What this phase accomplishes}}

**Tasks**
- [ ] TASK-02-01: {{Atomic task}}
- [ ] TASK-02-02: {{Atomic task}}

**File Changes**
- `path/to/file` ({{create|modify}}): {{What specifically to add or change — and what to leave alone}}

**Function Signatures**
- `function_name(param: Type) -> ReturnType` — {{one-line description}}

**Test Specs**
- {{`call_or_scenario(exact input values)`}} → {{exact expected output}}

**Dependencies**
- {{Internal or external dependency, or `None`}}

**Exit Criteria**
- [ ] {{Verifiable outcome}}
- [ ] {{Verifiable outcome}}

**Phase Risks**
- **RISK-02-01:** {{Risk and mitigation}}

### PHASE-03 - {{Phase Name or delete this section if not needed}}
**Goal**
{{What this phase accomplishes}}

**Tasks**
- [ ] TASK-03-01: {{Atomic task}}

**File Changes**
- `path/to/file` ({{create|modify}}): {{Specific change}}

**Function Signatures**
- {{Signature, or `None — no code interfaces change in this phase.`}}

**Test Specs**
- {{Spec, or `None — no testable behavior changes in this phase.`}}

**Dependencies**
- {{Internal or external dependency, or `None`}}

**Exit Criteria**
- [ ] {{Verifiable outcome}}

**Phase Risks**
- **RISK-03-01:** {{Risk and mitigation}}

## Gotchas
<!-- Global traps the implementer might hit: off-by-one risks, unit/currency/timezone confusions, naming convention traps, common mistakes for this type of work, non-obvious project decisions that affect implementation. -->
- {{Gotcha the executor would otherwise discover the hard way}}
- If none: `None identified.`

## Verification Strategy
<!-- Every item must be copy-paste runnable in a shell wherever possible — never a tool-specific instruction. State the exact expected result. -->
- **TEST-001:** {{Runnable command}} → {{exact expected result}}
- **MANUAL-001:** {{Manual validation step}}
- **OBS-001:** {{Logging, metrics, rollout, or monitoring check when relevant}}

## Risks and Alternatives
- **RISK-001:** {{Cross-phase risk and mitigation}}
- **ALT-001:** {{Alternative approach and why it was not chosen}}

## Suggested Next Step
{{Usually: execute PHASE-01; each phase's exit criteria are verifiable before the next begins.}}
