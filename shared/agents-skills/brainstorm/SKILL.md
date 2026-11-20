---
name: brainstorm
description: This skill should be used when the user explicitly invokes `/brainstorm` to shape an open idea or feature before any plan exists, through an interview grounded in the current repo, one question per turn with a recommended answer each, saved as a brainstorm markdown in `research/` that the `/plan` skill ingests automatically. Not for stress-testing a plan or decision already held. `--ui` runs the interview on a local browser page with prototypes and diagrams.
argument-hint: "[idea, problem, or feature] [--depth quick|standard|deep] [--auto] [--ui]"
disable-model-invocation: true
allowed-tools:
  - Bash
  - Read
  - Write
  - Glob
  - Grep
  - task
  - question
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

- Run only on explicit `/brainstorm`.
- Treat `$ARGUMENTS` as the subject, minus any `--depth`, `--auto`, or `--ui` flag.
- If `$ARGUMENTS` is empty, infer the subject from the immediately preceding user
  request only when it is obvious; otherwise ask for the subject and stop.

## Depth Tiers

Parse an optional `--depth` flag from `$ARGUMENTS`. Default to `standard`.

- `quick`: ~5-8 questions. One framing question, then the highest-leverage decisions only.
- `standard`: ~12-18 questions. Full framing plus the main design-tree branches.
- `deep`: 30-50 questions. Exhaustively walk every branch and resolve every dependency.

Treat counts as targets, not quotas. Stop early when the design is genuinely resolved;
do not invent questions to hit a number.

## Unattended Mode (`--auto`)

Parse an optional `--auto` flag from `$ARGUMENTS`. When present, the session is
unattended (no human to answer pickers):

- NEVER call the `question` tool — a rendered prompt blocks the session indefinitely.
- Run the same framing and design-tree interrogation internally: formulate each
  question, formulate the option you would have marked "(Recommended)", and adopt it
  as the answer.
- Record every self-answered question as a normal `DEC-xxx` entry with its rationale,
  suffixed `(auto-selected)`, so a reviewer can see which decisions were never
  human-confirmed.
- Anything that genuinely only the user can answer goes to `## Open Questions` with a
  recommended default as usual — do not stop to wait for input under any circumstances.
- If `$ARGUMENTS` has no subject, do not ask for one: abort and say so.
- Everything else (grounding subagent, depth tiers, output contract) is unchanged.

## Visual Mode (`--ui`)

Parse an optional `--ui` flag. When present, steps 3-5 run on a local browser page
instead of in the terminal, using the `grill-with-ui` skill: each question is a card with
lettered options, the recommendation outlined, rating chips per option, a discussion thread
per question, **Explore deeper** (a pros/cons table) and **Visualize** (an HTML prototype
of the design so far, or an architecture/flow diagram). The user stages answers in any
order and ships them with one **Send to Agent**.

- **Preconditions:** the `grill-with-ui` skill is installed and `node --version` is 20 or
  newer. If either fails, say so in one line and run the normal terminal interview.
- **`--auto` wins:** with both flags there is nobody to click the page; ignore `--ui` and
  say so.
- **Mechanics come from `grill-with-ui`:** load that skill and follow its sections for
  starting the server, patching `state.json`, listening (persistent monitor or wait mode,
  whichever this harness supports), handling sends, Explore, Visualize, and terminal
  input. This section only overrides *what* is asked and *what* gets written.

Overrides, in order:

1. **Before starting:** finish steps 1-2 (parse, repo grounding) as usual, and compute the
   brainstorm file path from the Output Contract now.
2. **Start:** run its `new` command with `--topic "<title>"`, `--intent "<one-sentence
   hypothesis of the real intent>"`, and `--doc "<the brainstorm file path, relative to
   the project root>"`.
3. **Round 1 = framing (step 3):** the 2-4 framing questions (real problem and who has it,
   what success looks like, candidate approaches), asked together when independent. Put
   `HYPOTHESIS: ... CONFIDENCE: ~N% — missing: ...` in the state's `note`, and update the
   note after every send, so progress stays visible on the page.
4. **Later rounds = grill (step 4):** follow `grill-with-ui`'s interview method (a frontier
   of up to three independent questions per round, `deps`, importance levels, ratings,
   `durable`, `terms`). Depth tiers count questions across all rounds. Repo-grounding
   findings go into question bodies; anything the repo already answers is recorded as a
   decision, never asked. The polite-agreement guard and the stop test still apply.
5. **Intent restate (step 5):** when the tree is walked, add one last question titled
   `Confirm intent` whose body gives Outcome, User, Why now, Success, and Out of scope as
   bold-labelled prose (the page renders inline markdown only), with options
   `A: Yes, write it up` (recommended) and `B: Refine` (the user says what in the thread or
   as free text), and no ratings (identical chips say nothing). Only an answer of A is a yes; fold a refinement in, re-ask, and once it
   is A set `note` to say Finish is the next step.
6. **Finish:** replace `grill-with-ui`'s design-doc layout with this skill's Output
   Template, written to the brainstorm file path:
   - every answered question becomes a `DEC-xxx` in order; a `durable` one also names the
     rejected options and why each lost (from its ratings and `explore` table);
   - `explore` tables feed `## Approaches Considered` (`ALT-xxx` for options that lost);
   - settled `terms` go in a `## Terms` section after `## Current vs Desired State`
     (term, definition, words to avoid);
   - deferred questions and threads that ended without a decision go to
     `## Open Questions`, each with its `rec` as the recommended default;
   - the frontmatter gains `mode: "ui"`, plus `visual: "<path>"` when a visual exists.
   Export a final visual next to the brainstorm file, same basename with `-visual.html` in
   place of `-brainstorm.md` (not under `docs/`). Then finish exactly as `grill-with-ui`
   says (patch `finished`, stop the server or monitor) and print both paths.

## Output Contract

- Save one markdown file in the active workspace.
- Use `research/` if it already exists; otherwise create `research/`.
- Use filename `YYYY-MM-DD_<slug>-brainstorm.md`.
- Derive `<slug>` as a 2-4 word ASCII kebab-case noun phrase from the subject.
- If the same-day filename already exists, append `-2`, `-3`, and so on.
- After writing, print the saved filepath and the exact next command: `/plan <slug>`.

This location and naming are intentional: `/plan` lists `research/**/*.md`, reads the
best matches, and records them under its `## Research Inputs`. The handoff is the
filesystem; the two skills stay decoupled.

## Procedure

### 1. Parse the request

- Extract the subject, the `--depth` value (default `standard`), the `--auto` flag, and the `--ui` flag.
- Derive the title and ASCII slug.

### 2. Ground the interview in the repo (subagent)

- If the workspace contains a codebase, use ONE read-only exploration subagent if
  available (otherwise explore inline) to map the surfaces relevant to the subject: existing modules, patterns, data shapes,
  routes/jobs, config, and anything the idea would reuse, extend, or collide with.
- Ask the subagent for conclusions only (relevant files + how they relate), not dumps.
- Also check whether `research/**/*.md` already holds a related brief; if so, read the
  1-2 closest matches and fold their findings in.
- If the workspace is greenfield or has no relevant code, skip exploration and say so.
- If the exploration subagent fails or returns nothing, proceed ungrounded and say so
  in the brainstorm's `Current state` line (e.g. `Ungrounded: repo exploration failed`).
- Use the findings to make questions concrete ("you already have `X` — reuse it or
  replace it?") instead of generic.

### 3. Frame (Socratic divergence)

In `--ui` mode, steps 3-5 run on the page; see Visual Mode.

Before grilling on solutions, establish the problem. Ask 2-4 open questions covering:
- The real problem and who has it; why solve it now.
- What success looks like; how you would know it worked.
- The candidate approaches worth considering at all.

Surface root causes here. For bug/diagnosis subjects, this stage often resolves the
issue before any design questions are needed.

### 4. Grill (exhaustive convergence)

Walk the design tree, resolving dependencies branch by branch.

- Ask ONE primary question per turn using the `question` tool (in `--auto`
  mode: answer it yourself per Unattended Mode instead of calling the tool).
- Make the recommended option the FIRST option and append "(Recommended)" to its label.
- Let each answer steer the next question — only ask what the previous answers make relevant.
- Group a tightly-coupled follow-up into the same call ONLY when it does not depend on the
  answer to the primary question.
- Record each resolved answer as a decision (`DEC-001`, `DEC-002`, ...).
- Keep going until the tier's target is met or the design is genuinely resolved.
- Track any question only the user can answer that stays unresolved; these become the
  brainstorm's `## Open Questions`, which `/plan` converts into binding-default
  assumptions (`ASM-xxx`) so the plan stays executable without the author.

### 5. Synthesize and save

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

## Problem & Why Now
<!-- seeds /plan ## Objective -->
{{The real problem, who has it, and why it matters now.}}

## Current vs Desired State
<!-- seeds /plan ## Context Snapshot -->
- **Current state:** {{What exists today, grounded in repo findings, or `Ungrounded: <why>` when exploration failed.}}
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

- One question per turn; never dump a wall of questions (in `--ui` mode, up to three
  independent questions per round).
- Every question carries a recommended answer, listed first and marked "(Recommended)".
- The user can always pick "Other" — treat that as the real answer and adapt.
- Prefer questions about product behavior, data handling, integrations, rollout, security
  or privacy posture, and acceptance criteria.
- Do not ask trivia, naming preferences, or anything the repo or `research/` already answers
  — answer those yourself from the subagent findings and record them as decisions.

## Quality Bar

Consider the brainstorm complete only when: the problem is framed, the high-leverage
decisions are resolved and recorded as `DEC-*`, repo grounding is reflected (or its
absence stated), `## Open Questions` holds only what truly needs the user, the file exists
under `research/`, and the printed `/plan <slug>` would produce a strong plan with little
further interrogation.

## Examples

- `/brainstorm add multi-tenant SSO onboarding`
- `/brainstorm refactor report generation into phase and final modes --depth deep`
- `/brainstorm why do failed sync jobs retry forever --depth quick`
