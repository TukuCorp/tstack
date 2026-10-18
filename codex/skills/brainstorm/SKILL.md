---
name: brainstorm
description: Shape an open idea or feature before any plan exists through a Socratic-then-exhaustive interview, asking one question at a time with a recommended answer, grounded in the current repository when relevant. Use when the user explicitly asks to brainstorm, explore an idea before building, resolve design decisions interactively, or invokes `/brainstorm`. Not for stress-testing a plan or decision the user already holds. Supports `--auto` for unattended runs (self-answers every question with its recommended option). Save the result under `research/`.
---

# Brainstorm

## Purpose

Reach genuine shared understanding of an idea *before* any code exists.
Run the deep, interactive interrogation, then write a single brainstorm markdown
file to `research/`.
Do not write implementation code or edit product files.

This skill combines two patterns: Socratic *divergence* (understand the real problem and
explore approaches first) and exhaustive *convergence* (walk the design tree one
question at a time, attaching a recommended answer to every question).

## Trigger

- Use this skill when the user explicitly asks to brainstorm or invokes `/brainstorm`.
- Treat the user's request as the subject, minus any `--depth` flag.
- If the request is empty, infer the subject from the immediately preceding user
  request only when it is obvious; otherwise ask for the subject and stop.

## Depth Tiers

Parse an optional `--depth` flag from the user's request. Default to `standard`.

- `quick`: ~5-8 questions. One framing question, then the highest-leverage decisions only.
- `standard`: ~12-18 questions. Full framing plus the main design-tree branches.
- `deep`: 30-50 questions. Exhaustively walk every branch and resolve every dependency.

Treat counts as targets, not quotas. Stop early when the design is genuinely resolved;
do not invent questions to hit a number.

## Unattended Mode (`--auto`)

Parse an optional `--auto` flag from the user's request. When present, the session is
unattended (no human to answer questions):

- NEVER ask the user anything: no structured input tool, no direct question. A pending
  question blocks the session indefinitely.
- Run the same framing and design-tree interrogation internally: formulate each
  question, formulate the option you would have marked "(Recommended)", and adopt it
  as the answer.
- Record every self-answered question as a normal `DEC-xxx` entry with its rationale,
  suffixed `(auto-selected)`, so a reviewer can see which decisions were never
  human-confirmed.
- Anything that genuinely only the user can answer goes to `## Open Questions` with a
  recommended default as usual. Do not stop to wait for input under any circumstances.
- If the request has no subject, do not ask for one: abort and say so.
- The intent restate (step 5) is self-confirmed: write it from the adopted answers and
  mark it `(auto-confirmed)` instead of waiting for a yes.
- Everything else (grounding exploration, depth tiers, output contract) is unchanged.

## Output Contract

- Save one markdown file in the active workspace.
- Use `research/` if it already exists; otherwise create `research/`.
- Use filename `YYYY-MM-DD_<slug>-brainstorm.md`.
- Derive `<slug>` as a 2-4 word ASCII kebab-case noun phrase from the subject.
- If the same-day filename already exists, append `-2`, `-3`, and so on.
- After writing, print the saved filepath.

## Procedure

### 1. Parse the request

- Extract the subject, the `--depth` value (default `standard`), and the `--auto` flag.
- Derive the title and ASCII slug.

### 2. Ground the interview in the repository

- If the workspace contains a codebase and subagents are available, use ONE read-only
  exploration subagent on a lighter, cheaper model than the main session (when the model
  can be chosen) to map the surfaces relevant to the subject: existing modules, patterns,
  data shapes, routes/jobs, config, and anything the idea would reuse, extend, or collide
  with. Mapping is token-heavy, so keep it off the main model.
- Ask the subagent for conclusions only (relevant files + how they relate), not dumps.
- If subagents are unavailable, perform the same focused repository inspection directly.
- Also check whether `research/**/*.md` already holds a related brief; if so, read the
  1-2 closest matches and fold their findings in.
- If the workspace is greenfield or has no relevant code, skip exploration and say so.
- If the exploration subagent fails or returns nothing, proceed ungrounded and say so
  in the brainstorm's `Current state` line (e.g. `Ungrounded: repo exploration failed`).
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

- Ask ONE primary question per turn. Use a structured question tool when the harness
  offers one; otherwise ask directly in chat. (In `--auto` mode: answer it yourself per Unattended Mode instead of asking.)
- Make the recommended option the FIRST option and append "(Recommended)" to its label.
- Let each answer steer the next question — only ask what the previous answers make relevant.
- Group a tightly-coupled follow-up into the same question ONLY when it does not depend on
  the answer to the primary question.
- Record each resolved answer as a decision (`DEC-001`, `DEC-002`, ...).
- Keep going until the tier's target is met or the design is genuinely resolved.
- Stop test: you are done when you can predict the user's answer to the next three
  questions you would ask. If several rounds pass and confidence is not rising, stop and
  say something foundational is missing, then reframe rather than grinding on.
- Track any question only the user can answer that stays unresolved; these become the
  brainstorm's `## Open Questions`, each with a recommended default so the work stays
  executable without the author.

### 5. Restate and confirm intent

Before writing anything, restate the intent in the user's own words, one line each:

```
- Outcome:      <what they get>
- User:         <who benefits>
- Why now:      <what changed>
- Success:      <how we know it worked>
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
- Save the file per the Output Contract and print the path.

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
- **Out of scope:** {{...}}

## Problem & Why Now
{{The real problem, who has it, and why it matters now.}}

## Current vs Desired State
- **Current state:** {{What exists today, grounded in repo findings, or `Ungrounded: <why>` when exploration failed.}}
- **Desired state:** {{What should exist after this work.}}
- **Key repo surfaces:** {{Files/modules/routes/jobs/tables the work touches, or `None (greenfield)`.}}

## Resolved Decisions
<!-- the grilled Q&A -->
- **DEC-001:** {{Decision}} — {{one-line rationale}}
- **DEC-002:** {{Decision}} — {{rationale}}

## Assumptions & Constraints
- **ASM-001:** {{Assumption}}
- **CON-001:** {{Constraint}}

## Approaches Considered
- **Chosen:** {{Approach}} — {{why}}
- **ALT-001:** {{Alternative}} — {{why not}}

## Out of Scope
- {{Explicit exclusion}}

## Open Questions
<!-- the few that survived. Use `None.` when fully resolved. -->
1. **Q-001:** {{Question only the user can answer}}
   - **Recommended default:** {{Reasonable default}}
   - **Why this matters:** {{What it changes}}
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
absence stated), `## Open Questions` holds only what truly needs the user, and the file
exists under `research/`.

## Examples

- `/brainstorm add multi-tenant SSO onboarding`
- `/brainstorm refactor report generation into phase and final modes --depth deep`
- `/brainstorm why do failed sync jobs retry forever --depth quick`
