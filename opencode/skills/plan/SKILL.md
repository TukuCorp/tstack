---
name: plan
description: This skill should be used when the user explicitly invokes `/plan` to turn a feature, refactor, bug fix, migration, or project idea into a detailed multi-phase markdown plan saved under `plans/` — self-contained and executable by any coding agent or engineer with zero shared context, using relevant repo context and `research/` briefs when available.
argument-hint: "[feature, refactor, bug, or project goal]"
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

The saved plan is a portable hand-off artifact. It must be executable by any coding
agent or engineer with zero shared context: no access to this conversation, no agent
instruction files (`AGENTS.md` and similar), no tool-specific features — only a
checkout of the repo and the plan file itself. Everything the executor needs lives
in the plan.

## Trigger

- Run only on explicit `/plan`.
- Treat `$ARGUMENTS` as the planning brief.
- If `$ARGUMENTS` is empty, infer the subject from the immediately preceding user request only when it is obvious.
- Otherwise, ask for the missing planning subject and stop.
- Never leave open questions in the plan. Resolve unknowns from the repo and `research/` first; anything genuinely unresolvable becomes a binding-default assumption (`ASM-xxx`) the executor applies (see `## Binding Defaults`).

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
- Be extremely explicit: specify units, currencies, time intervals, and naming conventions by name. When in doubt, over-explain rather than under-explain.
- Tool-agnostic language: never reference this conversation or decisions made in it — restate everything the executor needs inside the plan; never include tool-specific instructions (subagents, skills, interactive question prompts, MCP tools) in the plan body; every command in the plan must be copy-paste runnable in a shell.
- If a detail cannot be derived reliably, record it as a binding-default assumption instead of guessing silently.

## Context Gathering

### 1. Read the minimum relevant repo context

- Inspect the smallest set of docs, config, and source files needed to understand the request.
- Prefer `README*`, product docs, routing/config files, and the implementation area directly related to the request.
- For large or unfamiliar repos, use one focused `explore` task to find likely files, then read only the strongest matches.

### 2. Derive Environment & Conventions

- Read `AGENTS.md`, `README*`, package manifests (`package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`, `Gemfile`, and similar), lockfiles, and CI config to extract: exact install, build, and test commands (full suite AND single test), stack and versions, lint/format expectations, naming conventions, and units/timezone/currency rules.
- Verify commands against the repo (scripts blocks, CI steps, Makefiles) rather than guessing.
- This section exists because the executor does NOT get agent instruction files or session context — the plan replaces them.
- Anything unverifiable becomes a binding-default assumption.

### 3. Use `research/` when available

- Check whether `research/` exists in the current workspace.
- If it exists, list `research/**/*.md`.
- Use request keywords to identify likely relevant briefs.
- Read the 1-3 best matches.
- If the request is broad, also read the most recent brief when it is topically close.
- INLINE the findings that shape the plan into `## Research Inputs`: 2-6 bullets per brief, copied into the plan body. Keep the brief's path as provenance only — the executor may not have `research/`.
- If a brainstorm brief lists resolved decisions, lift them into the plan as `DEC-xxx` entries; convert its open questions into binding-default assumptions.
- If no relevant brief exists, say so plainly.
- Do not pad the section.

### 4. Resolve uncertainty

- Search the codebase and research notes first.
- A genuine unknown that survives both becomes an `ASM-xxx` with a binding default — never an open question.

## Binding Defaults

- The plan ships with zero open questions; a foreign executor has no way to ask the author anything.
- Every unresolved, project-specific unknown becomes an assumption with an explicit default the executor MUST apply: `**ASM-00N:** {{unknown}} — **BINDING DEFAULT:** {{what the executor applies}}`.
- Choose the most conventional, lowest-risk default; the author can edit the ASM line before handing the plan off.

## Build Procedure

1. Parse `$ARGUMENTS` into a concrete planning subject.
2. Derive a concise plan title and ASCII slug.
3. Select the output directory using the priority order in `## Output Contract`.
4. Gather the minimum repo context needed to avoid vague planning.
5. Derive Environment & Conventions from the repo.
6. Inspect `research/` and inline the most relevant findings.
7. Decide the phase layout, usually 2-6 phases with explicit dependencies.
8. Read `assets/plan-template.md` and use it as the exact output skeleton. If the template file is missing, stop and report the missing path — do not reconstruct it from memory.
9. Fill every section with request-specific and repo-specific detail at hand-off precision (see `## Phase Rules`).
10. Run the `## Portability Audit`; fix violations and re-check until clean.
11. Save the final markdown plan file and print its path.

## Required Plan Structure

- The skeleton is `assets/plan-template.md` — the single authoritative template. Do not duplicate it here or elsewhere.
- Keep the top-level sections and subsection names exactly.
- Fill every placeholder; remove instructional placeholder comments from the final output.
- `## Specification` is conditional: include it only when real formulas or cross-phase decision logic exist; delete it otherwise.
- Per-phase **Function Signatures** and **Test Specs** may state `None — no code interfaces change in this phase.` / `None — no testable behavior changes in this phase.` only when genuinely inapplicable.

## Phase Rules

- Give each phase a clear goal.
- Break each phase into atomic tasks that another agent could execute without this conversation.
- **File Changes:** for each file, the exact path, whether to `create` or `modify`, what specifically to add or change, and what to leave alone.
- **Function Signatures:** complete interfaces — parameter names, types, return types, and a one-line description of what each returns.
- **Test Specs:** concrete scenarios with literal inputs and expected outputs, edge cases spelled out — not "write tests for X".
- Record dependencies explicitly.
- Add exit criteria that can be verified.
- Add phase-specific risks when they materially change execution.
- Collect cross-cutting implementation traps (off-by-one risks, unit/currency/timezone confusions, naming traps, non-obvious project decisions) in the global `## Gotchas` section.

## Portability Audit

Hard gate: run this checklist on the drafted plan BEFORE writing the file. Fix every violation and re-check until all six pass.

1. No references to the authoring conversation, session, or decisions-by-allusion — everything the executor needs is restated in the plan.
2. No tool-specific instructions anywhere in the plan body.
3. Every command is copy-paste runnable in a shell.
4. Every file path named in File Changes exists in the repo, or is explicitly marked `create`.
5. Every unknown is backed by a binding-default `ASM-xxx`.
6. Every template section is present and filled, or carries its documented empty state (`## Specification` deleted when not applicable).

## Verification Rules

- Include automated tests, manual checks, data checks, rollout checks, or observability checks as appropriate.
- Express every verification item as a copy-paste runnable shell command with its exact expected result wherever possible; never as a tool-specific instruction.
- Tie verification items to specific parts of the plan.

## Quality Bar

- Consider the plan complete only when: the saved file exists; the phases are concrete, sequenced, and at hand-off precision (File Changes, Function Signatures, Test Specs); research findings are inlined or explicitly absent; Environment & Conventions is verified against the repo; the Portability Audit passed; and a foreign agent with only the repo and the plan could execute the work without any extra conversation.

## Examples

- `/plan add multi-tenant SSO onboarding`
- `/plan refactor report generation into phase and final modes`
- `/plan fix retry behavior for failed sync jobs`
