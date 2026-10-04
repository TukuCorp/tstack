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

## Research Inputs
- {{research/file.md}} - {{How this brief changes scope, sequencing, design, or risk}}
- {{research/file.md}} - {{How this brief changes testing, rollout, or tradeoffs}}
- If none: `No applicable research briefs were found in research/.`

## Assumptions and Constraints
- **ASM-001:** {{Assumption grounded in repo context or request}}
- **CON-001:** {{Constraint that limits the solution}}
- **DEC-001:** {{Known decision already fixed by the current system or request}}

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
- [ ] TASK-01-01: {{Atomic task}}
- [ ] TASK-01-02: {{Atomic task}}

**Files / Surfaces**
- `path/to/file` - {{Why it changes or why it must be inspected}}
- `path/to/area` - {{Why it matters}}

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

**Files / Surfaces**
- `path/to/file` - {{Why it changes or why it must be inspected}}
- `path/to/area` - {{Why it matters}}

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
- [ ] TASK-03-02: {{Atomic task}}

**Files / Surfaces**
- `path/to/file` - {{Why it changes or why it must be inspected}}
- `path/to/area` - {{Why it matters}}

**Dependencies**
- {{Internal or external dependency, or `None`}}

**Exit Criteria**
- [ ] {{Verifiable outcome}}
- [ ] {{Verifiable outcome}}

**Phase Risks**
- **RISK-03-01:** {{Risk and mitigation}}

## Verification Strategy
- **TEST-001:** {{Automated test, script, or command to run}}
- **MANUAL-001:** {{Manual validation step}}
- **OBS-001:** {{Logging, metrics, rollout, or monitoring check when relevant}}

## Risks and Alternatives
- **RISK-001:** {{Cross-phase risk and mitigation}}
- **ALT-001:** {{Alternative approach and why it was not chosen}}

## Grill Me
<!-- Keep 0-6 questions only. Replace this section with `No open clarification questions.` when fully resolved. -->
1. **Q-001:** {{Question that only the user can answer}}
   - **Recommended default:** {{Reasonable default if the user does not override it}}
   - **Why this matters:** {{What part of the plan changes}}
   - **If answered differently:** {{What changes in scope, sequencing, or verification}}

## Suggested Next Step
{{Usually: answer the Grill Me questions, update the plan, then begin implementation.}}
