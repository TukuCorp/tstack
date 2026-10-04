---
name: brainstorm
description: Interrogate an idea, problem, or feature through a Socratic-then-exhaustive interview, asking one question at a time with a recommended answer, grounded in the current repository when relevant. Use when the user explicitly asks to brainstorm, explore an idea before planning, resolve design decisions interactively, or invokes `/brainstorm`. Supports `--auto` for unattended runs (self-answers every question with its recommended option). Save the result under `research/` for the `plan` skill to consume.
---

# Brainstorm

## Purpose

Reach genuine shared understanding of an idea *before* any plan or code exists.
Run the deep, interactive interrogation that `/plan` deliberately avoids, then
write a single brainstorm markdown file to `research/`.
Do not write implementation code, edit product files, or produce a plan.

This skill is the front half of `/brainstorm` -> `/plan` -> implementation.
It combines two patterns: Socratic *divergence* (understand the real problem and
explore approaches first) and exhaustive *convergence* (walk the design tree one
question at a time, attaching a recommended answer to every question).

## Trigger

- Use this skill when the user explicitly asks to brainstorm or invokes `/brainstorm`.
- Treat the user's request as the subject, minus any `--depth` flag.
- If the request is empty, infer the subject from the immediately preceding user
  request only when it is obvious; otherwise ask for the subject and stop.

## Depth Tiers

Parse an optional `--depth` flag from the request. Default to `standard`.

- `quick`: ~5-8 questions. One framing question, then the highest-leverage decisions only.
- `standard`: ~12-18 questions. Full framing plus the main design-tree branches.
- `deep`: 30-50 questions. Exhaustively walk every branch and resolve every dependency.

Treat counts as targets, not quotas. Stop early when the design is genuinely resolved;
do not invent questions to hit a number.

## Unattended Mode (`--auto`)

Parse an optional `--auto` flag from the request. When present, the session is
unattended (no human to answer questions):

- NEVER ask the user anything — no structured input tool, no direct question; a
  rendered prompt blocks the session indefinitely.
- Run the same framing and design-tree interrogation internally: formulate each
  question, formulate the option you would have marked "(Recommended)", and adopt it
  as the answer.
- Record every self-answered question as a normal `DEC-xxx` entry with its rationale,
  suffixed `(auto-selected)`, so a reviewer can see which decisions were never
  human-confirmed.
- Anything that genuinely only the user can answer goes to `## Open Questions` with a
  recommended default as usual — do not stop to wait for input under any circumstances.
- If the request has no subject, do not ask for one: abort and say so.
- The intent restate (step 5) is self-confirmed: write it from the adopted answers and
  mark it `(auto-confirmed)` instead of waiting for a yes.
- Everything else (grounding exploration, depth tiers, output contract) is unchanged.

## Output Contract

- Save one markdown file in the active workspace.
- Use `research/` if it already exists; otherwise create `research/`.
- Use filename `YYYY-MM-DD_<slug>-brainstorm.md`.
- Derive `<slug>` as a 2-6 word ASCII kebab-case noun phrase from the subject.
- If the same-day filename already exists, append `-2`, `-3`, and so on.
- After writing, print the saved filepath and the exact next command: `/plan <slug>`.

This location and naming are intentional: `/plan` lists `research/**/*.md`, reads the
best matches, and records them under its `## Research Inputs`. The handoff is the
filesystem; the two skills stay decoupled.

## Procedure

### 1. Parse the request

- Extract the subject, the `--depth` value (default `standard`), and the `--auto` flag.
- Derive the title and ASCII slug.

### 2. Ground the interview in the repository

- If the workspace contains a codebase and subagents are available, use one read-only exploration subagent to
  map the surfaces relevant to the subject: existing modules, patterns, data shapes,
  routes/jobs, config, and anything the idea would reuse, extend, or collide with.
- Ask the subagent for conclusions only (relevant files + how they relate), not dumps.
- If subagents are unavailable, perform the same focused repository inspection directly.
- Also check whether `research/**/*.md` already holds a related brief; if so, read the
  1-2 closest matches and fold their findings in.
- If the workspace is greenfield or has no relevant code, skip exploration and say so.
- Use the findings to make questions concrete ("you already have `X` — reuse it or
  replace it?") instead of generic.

### 3. Frame (Socratic divergence)

Before grilling on solutions, establish what the user actually wants, which is often
not what they literally asked for ("a dashboard" may really mean "a list").

- Open with a one-sentence hypothesis of the real intent and an honest confidence
  number, e.g. `HYPOTHESIS: ... CONFIDENCE: ~30% — missing: who it's for, what success is`.
  Below ~70%, always name what is still missing.
- Then ask 2-4 questions, one at a time, covering:
  - The real problem and who has it; why solve it now.
  - What success looks like; how you would know it worked.
  - The binding constraint, and which value wins when two conflict (e.g. cost vs speed).
  - The candidate approaches worth considering at all.
- Restate the updated hypothesis and confidence after each answer so progress is visible.
- Listen for "should want" answers: best-practice talk without specifics ("scalable",
  "clean", "modern"), deference to convention ("the standard way"), or "I should
  probably...". When you hear one, ask: "If you didn't have to justify this to anyone,
  what would you actually want?"

Surface root causes here. For bug/diagnosis subjects, this stage often resolves the
issue before any design questions are needed.

### 4. Grill (exhaustive convergence)

Walk the design tree, resolving dependencies branch by branch.

- Ask one primary question per turn. Use a structured user-input tool when available; otherwise ask the question directly. (In `--auto` mode: answer it yourself per Unattended Mode instead of asking.)
- Make the recommended option the FIRST option and append "(Recommended)" to its label.
- Let each answer steer the next question — only ask what the previous answers make relevant.
- Group a tightly-coupled follow-up into the same call ONLY when it does not depend on the
  answer to the primary question.
- Record each resolved answer as a decision (`DEC-001`, `DEC-002`, ...).
- Keep going until the tier's target is met or the design is genuinely resolved.
- Stop test: you are done when you can predict the user's answer to the next three
  questions you would ask. If several rounds pass and confidence is not rising, stop and
  say something foundational is missing, then reframe rather than grinding on.
- Track any question only the user can answer that stays unresolved; these become the
  brainstorm's `## Open Questions`, which `/plan` converts into binding-default
  assumptions (`ASM-xxx`) so the plan stays executable without the author.

### 5. Restate and confirm intent

Before writing anything, restate the intent in the user's own words, one line each:

```
- Outcome:      <what they get>
- User:         <who benefits>
- Why now:      <what changed>
- Success:      <how we know it worked>
- Constraint:   <the binding limit>
- Out of scope: <what we are explicitly not doing>
Yes / no / refine?
```

- `Out of scope` is mandatory: silent disagreement about non-goals causes half of
  misalignment.
- Require an explicit yes. "Whatever you think", "sounds good", or "sure, let's go" are
  not a yes: re-ask as a choice between two concrete options, or ask "anything you'd
  refine?". Fold corrections in and restate until you get a clear yes.

### 6. Synthesize and save

- Fill the output template below from the framing answers, resolved decisions, and findings.
- Map sections so `/plan` can lift them directly (see comments in the template).
- Save the file per the Output Contract and print the path plus `/plan <slug>`.

## Output Template

```markdown
---
title: "{{TITLE}}"
date: "{{DATE}}"
type: "brainstorm"
depth: "{{quick|standard|deep}}"
source_request: "{{ORIGINAL_SUBJECT}}"
slug: "{{SLUG}}"
---

# Brainstorm: {{TITLE}}

## Statement of Intent
<!-- the confirmed restate from step 5; mark (auto-confirmed) in --auto mode -->
- **Outcome:** {{...}}
- **User:** {{...}}
- **Why now:** {{...}}
- **Success:** {{...}}
- **Constraint:** {{...}}
- **Out of scope:** {{...}}

## Problem & Why Now
<!-- seeds /plan ## Objective -->
{{The real problem, who has it, and why it matters now.}}

## Current vs Desired State
<!-- seeds /plan ## Context Snapshot -->
- **Current state:** {{What exists today, grounded in repo findings.}}
- **Desired state:** {{What should exist after this work.}}
- **Key repo surfaces:** {{Files/modules/routes/jobs/tables the work touches, or `None (greenfield)`.}}

## Resolved Decisions
<!-- the grilled Q&A; /plan lifts these directly as fixed DEC-xxx entries -->
- **DEC-001:** {{Decision}} — {{one-line rationale}}
- **DEC-002:** {{Decision}} — {{rationale}}

## Assumptions & Constraints
<!-- seeds /plan ## Assumptions and Constraints -->
- **ASM-001:** {{Assumption}}
- **CON-001:** {{Constraint}}

## Approaches Considered
<!-- seeds /plan ## Risks and Alternatives -->
- **Chosen:** {{Approach}} — {{why}}
- **ALT-001:** {{Alternative}} — {{why not}}

## Out of Scope
- {{Explicit exclusion}}

## Open Questions
<!-- the few that survived; /plan converts each into a binding-default assumption (ASM-xxx), using Recommended default as the binding default. Use `None.` when fully resolved. -->
1. **Q-001:** {{Question only the user can answer}}
   - **Recommended default:** {{Reasonable default}}
   - **Why this matters:** {{What it changes}}

## Suggested Next Step
Run `/plan {{SLUG}}` to turn this into a multi-phase implementation plan.
```

## Interview Rules

- One question per turn; never dump a wall of questions.
- Every question carries a recommended answer, listed first and marked "(Recommended)".
- The user can always pick "Other" — treat that as the real answer and adapt.
- Guard against polite agreement: now and then recommend something you expect the user
  to push back on, and never treat "whatever you think" as a decision.
- Prefer questions about product behavior, data handling, integrations, rollout, security
  or privacy posture, and acceptance criteria.
- Do not ask trivia, naming preferences, or anything the repository or `research/` already answers; resolve those from the available evidence and record them as decisions.

## Quality Bar

Consider the brainstorm complete only when: the intent restate got an explicit yes
(or is marked auto-confirmed), the problem is framed, the high-leverage
decisions are resolved and recorded as `DEC-*`, repo grounding is reflected (or its
absence stated), `## Open Questions` holds only what truly needs the user, the file exists
under `research/`, and the printed `/plan <slug>` would produce a strong plan with little
further interrogation.

## Examples

- `/brainstorm add multi-tenant SSO onboarding`
- `/brainstorm refactor report generation into phase and final modes --depth deep`
- `/brainstorm why do failed sync jobs retry forever --depth quick`
