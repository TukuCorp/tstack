---
name: plan
description: "Turn a feature, refactor, bug fix, migration, or project idea into a detailed multi-phase markdown plan saved under .hermes/plans/ — self-contained and executable by any coding agent or engineer with zero shared context. Planning only, no execution."
version: 3.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [planning, plan-mode, implementation, workflow, design, documentation, handoff]
    related_skills: [plan-audit, test-driven-development, agent-plans-execution]
---

# Plan

## Purpose

Create a concrete, multi-phase implementation plan for the active workspace.
Write the plan file only.

- Do not implement code.
- Do not edit project files except the plan markdown file.
- Do not run mutating terminal commands, commit, push, or perform external actions.
- You may inspect the repo or other context with read-only commands/tools when needed.

The saved plan is a portable hand-off artifact. It must be executable by any coding
agent or engineer with zero shared context: no access to this conversation, no agent
instruction files (`AGENTS.md`, `.hermes.md`, and similar), no tool-specific features —
only a checkout of the repo and the plan file itself. Everything the executor needs
lives in the plan.

## Trigger

- Use this skill when the user wants a plan instead of execution, or invokes `/plan`.
- Treat the user's request as the planning brief.
- If no explicit instruction accompanies the request, infer the task from the current conversation context only when it is obvious.
- If it is genuinely underspecified, ask a brief clarifying question instead of guessing.
- Never leave open questions in the plan itself. Resolve unknowns from the repo and `research/` first; anything genuinely unresolvable becomes a binding-default assumption (`ASM-xxx`) the executor applies (see `## Binding Defaults`).

## Output Contract

- Save the plan with `write_file` under `.hermes/plans/` in the active workspace, creating the directory if needed.
- Treat the path as relative to the active working directory / backend workspace, so the plan stays with the workspace on local, docker, ssh, modal, and daytona backends.
- If the runtime provides a specific target path, use that exact path instead.
- Use filename `YYYY-MM-DD-<slug>-plan.md`.
- Derive `<slug>` as a 2-6 word ASCII kebab-case noun phrase from the request.
- If the same-day filename already exists, append `-2`, `-3`, and so on.
- After saving, reply briefly with what you planned and the saved path.

## Planning Principles

- Write for another agent or engineer with zero shared context.
- Prefer deterministic, specific language over abstract advice.
- Prefer 2-6 phases; use fewer only when the work is genuinely small.
- Use exact file paths, modules, routes, jobs, tables, interfaces, commands, or operational surfaces when the repo makes them knowable.
- Be extremely explicit: specify units, currencies, time intervals, and naming conventions by name. When in doubt, over-explain rather than under-explain.
- Tool-agnostic language: never reference this conversation or decisions made in it — restate everything the executor needs inside the plan; never include tool-specific instructions (subagents, skills, interactive prompts, MCP tools) in the plan body; every command in the plan must be copy-paste runnable in a shell.
- If a detail cannot be derived reliably, record it as a binding-default assumption instead of guessing silently.

## Context Gathering

### 1. Read the minimum relevant repo context

- Inspect the smallest set of docs, config, and source files needed to understand the request (`read_file`, `search_files`).
- Prefer `README*`, product docs, routing/config files, and the implementation area directly related to the request.
- For large or unfamiliar repos, run one focused exploration pass to find likely files, then read only the strongest matches.

### 2. Derive Environment & Conventions

- Read `AGENTS.md`, `README*`, package manifests (`package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`, `Gemfile`, and similar), lockfiles, and CI config to extract: exact install, build, and test commands (full suite AND single test), stack and versions, lint/format expectations, naming conventions, and units/timezone/currency rules.
- Verify commands against the repo (scripts blocks, CI steps, Makefiles) rather than guessing.
- This section exists because the executor does NOT get agent instruction files or session context — the plan replaces them.
- Anything unverifiable becomes a binding-default assumption.

### 3. Use `research/` when available

- Check whether `research/` exists in the current workspace.
- If it exists, list `research/**/*.md`, identify likely relevant briefs by request keywords, and read the 1-3 best matches.
- INLINE the findings that shape the plan into `## Research Inputs`: 2-6 bullets per brief, copied into the plan body. Keep the brief's path as provenance only — the executor may not have `research/`.
- If a brainstorm brief lists resolved decisions, lift them into the plan as `DEC-xxx` entries; convert its open questions into binding-default assumptions.
- If no relevant brief exists, say so plainly. Do not pad the section.

### 4. Resolve uncertainty

- Search the codebase and research notes first.
- A genuine unknown that survives both becomes an `ASM-xxx` with a binding default — never an open question.

## Binding Defaults

- The plan ships with zero open questions; a foreign executor has no way to ask the author anything.
- Every unresolved, project-specific unknown becomes an assumption with an explicit default the executor MUST apply: `**ASM-00N:** {{unknown}} — **BINDING DEFAULT:** {{what the executor applies}}`.
- Choose the most conventional, lowest-risk default; the author can edit the ASM line before handing the plan off.

## Build Procedure

1. Parse the request into a concrete planning subject.
2. Derive a concise plan title and ASCII slug.
3. Gather the minimum repo context needed to avoid vague planning.
4. Derive Environment & Conventions from the repo.
5. Inspect `research/` and inline the most relevant findings.
6. Decide the phase layout, usually 2-6 phases with explicit dependencies.
7. Read `templates/plan-template.md` (relative to this skill directory) and use it as the exact output skeleton. If the template file is missing, stop and report the missing path — do not reconstruct it from memory.
8. Fill every section with request-specific and repo-specific detail at hand-off precision (see `## Phase Rules`).
9. Run the `## Portability Audit`; fix violations and re-check until clean.
10. Save the final markdown plan file and report its path.

## Required Plan Structure

- The skeleton is `templates/plan-template.md` — the single authoritative template. Do not duplicate it here or elsewhere.
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

## Execution Handoff

After saving the plan, offer execution: the plan is designed to be handed to any coding
agent (or executed here across sessions). For orchestrated runs, the `agent-plans-execution`
skill can drive an autonomous coding agent through the phases; plans in this format carry
zero open questions, so no pre-answering step is required.
