---
name: plan
description: This skill should be used when the user explicitly invokes `/plan` to turn a feature, refactor, bug fix, migration, or project idea into a detailed multi-phase markdown plan saved under `plans/`, using relevant repo context and `research/` briefs when available.
argument-hint: "[feature, refactor, bug, or project goal]"
disable-model-invocation: true
allowed-tools:
  - Bash
  - Read
  - Write
  - Glob
  - Grep
  - Task
---

# Plan

## Purpose

Create a concrete, multi-phase implementation plan for the active workspace.
Write the plan file only.
Do not write implementation code, edit product files, or start execution.

## Trigger

- Run only on explicit `/plan`.
- Treat `$ARGUMENTS` as the planning brief.
- If `$ARGUMENTS` is empty, infer the subject from the immediately preceding user request only when it is obvious.
- Otherwise, ask for the missing planning subject and stop.
- Prefer embedding unresolved project-specific clarifications inside the plan's `## Grill Me` section instead of interrupting the flow with live follow-up questions.

## Output Contract

- Save one markdown plan in the active workspace.
- Use `plans/` if it already exists.
- Otherwise use `docs/plans/` if that directory already exists.
- Otherwise create `plans/`.
- Use filename `YYYY-MM-DD-<slug>-plan.md`.
- Derive `<slug>` as a 2-6 word ASCII kebab-case noun phrase from the request.
- If the same-day filename already exists, append `-2`, `-3`, and so on.
- Print the saved filepath after writing the plan.

## Planning Principles

- Write for another agent or engineer with zero shared context.
- Prefer deterministic, specific language over abstract advice.
- Prefer 2-6 phases; use fewer only when the work is genuinely small.
- Use exact file paths, modules, routes, jobs, tables, interfaces, commands, or operational surfaces when the repo makes them knowable.
- If a detail cannot be derived reliably, surface it in `## Grill Me` instead of guessing.
- Ask fewer than six questions whenever possible.
- Never exceed six `## Grill Me` questions.
- If a question can be answered by exploring the repo or `research/`, answer it directly and record the conclusion in the plan instead of surfacing the question.

## Context Gathering

### 1. Read the minimum relevant repo context

- Inspect the smallest set of docs, config, and source files needed to understand the request.
- Prefer `README*`, product docs, routing/config files, and the implementation area directly related to the request.
- For large or unfamiliar repos, use one focused `explore` task to find likely files, then read only the strongest matches.

### 2. Use `research/` when available

- Check whether `research/` exists in the current workspace.
- If it exists, list `research/**/*.md`.
- Use request keywords to identify likely relevant briefs.
- Read the 1-3 best matches.
- If the request is broad, also read the most recent brief when it is topically close.
- Extract only reusable findings that affect scope, sequencing, architecture, risk, verification, or tradeoffs.
- Record every applied brief in `## Research Inputs`.
- If no relevant brief exists, say so plainly.
- Do not pad the section.

### 3. Resolve uncertainty before writing questions

- Search the codebase and research notes first.
- Keep a question only when the answer is project-specific, product-specific, operationally sensitive, or genuinely unknowable from available context.

## Build Procedure

1. Parse `$ARGUMENTS` into a concrete planning subject.
2. Derive a concise plan title and ASCII slug.
3. Select the output directory using the priority order in `## Output Contract`.
4. Gather the minimum repo context needed to avoid vague planning.
5. Inspect `research/` and absorb the most relevant available briefs.
6. Decide the phase layout, usually 2-6 phases with explicit dependencies.
7. Read `assets/plan-template.md` and use it as the output skeleton.
8. Fill every section with request-specific and repo-specific details.
9. Add `## Grill Me` questions only for truly unresolved project decisions.
10. Save the final markdown plan file and print its path.

## Required Plan Structure

- Start from `assets/plan-template.md`.
- Keep the top-level sections and subsection names exactly.
- Fill every placeholder.
- Remove instructional placeholder comments from the final output.

## Phase Rules

- Give each phase a clear goal.
- Break each phase into atomic tasks that another agent could execute without this conversation.
- Name the concrete files or operational surfaces touched in that phase whenever known.
- Record dependencies explicitly.
- Add exit criteria that can be verified.
- Add phase-specific risks when they materially change execution.

## Grill Me Rules

- Use `## Grill Me` for unresolved choices only.
- Include 0-6 numbered questions.
- For each question, include `Recommended default`, `Why this matters`, and `If answered differently`.
- Prefer questions about product behavior, rollout strategy, data migration handling, security or privacy posture, external integrations, and acceptance criteria.
- Do not ask trivia, naming preference, or easily derivable implementation questions.
- If no clarifications are needed, write `No open clarification questions.`

## Verification Rules

- Include automated tests, manual checks, data checks, rollout checks, or observability checks as appropriate.
- Tie verification items to specific parts of the plan.

## Quality Bar

- Consider the plan complete only when the saved file exists, the phases are concrete and sequenced, research inputs are incorporated or explicitly absent, `## Grill Me` has at most six high-leverage questions, and another agent could execute the work without extra conversation.

## Examples

- `/plan add multi-tenant SSO onboarding`
- `/plan refactor report generation into phase and final modes`
- `/plan fix retry behavior for failed sync jobs`
