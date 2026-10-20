---
name: reflect
description: "Audit how well installed skills perform by scoring recent local agent conversations (Claude Code, Codex, Hermes) for efficiency, code quality, procedure compliance and verbosity, then draft skill edits and an HTML report. With `--session`, review only the current session with three parallel reviewer subagents and route durable learnings into skill edits (or a backlog entry in lessons.md). Use only when the user says \"reflect\" or \"/reflect\"."
version: 2.0.0
author: Lauren Tan (pstack) and Warp skill-doctor, adapted
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [reflection, learnings, skill-maintenance, review, subagents, audit]
    related_skills: [hermes-agent-skill-authoring]
---

# Reflect

Two modes. Both end in proposed skill edits that the user approves before anything changes.

| Mode | Trigger | Looks at | Output |
|---|---|---|---|
| Audit (default) | `/reflect` | Recent conversations across the chosen repos and harnesses | Letter-graded HTML report, drafted skill diffs |
| Session | `/reflect --session` | The current session only | Accepted / Rejected / Backlog table, skill edits |

Invoke only when the user says "reflect" or "/reflect". Without `--session`, run audit mode. Skip either mode when the work is trivial or already covered by an existing skill that was followed correctly. One-offs are not learnings.

## Audit mode

`read_file` `references/audit-mode.md` and follow it. It collects sessions with `scripts/collect_sessions.py` (run through the terminal tool), scores them against `scorers/*.md`, drafts diffs under the edit gate in `references/audit-edit-gate.md`, and renders `reports/reflect-<date>/report.html` with `scripts/render_report.py`. Use `delegate_task` for the scoring batches. Then continue at "Applying approved edits" below.

## Session mode

Mine the current session for durable learnings, then route them into skill edits. If the user gave a focus, pass it to every reviewer.

### 1. Build a session digest

Write a tight digest of this session with `write_file` to a temp file, `reflect-digest.txt`, one line per event: `user: <request or correction>`, `assistant: <decision or claim>`, `assistant TOOL <name>: <key arguments>`, `RESULT: <outcome or error>`. Cover every user correction, every decision and its stated reason, every tool failure and retry, and every skill used. Quote corrections verbatim. Keep it under ~60 KB. Use `session_search` only to recover parts of this session that are no longer in context. Do not pull in other sessions.

Also `read_file` the project's `lessons.md` if one exists, so reviewers don't resurface lessons already recorded.

### 2. Spawn three reviewers in parallel

Three `delegate_task` calls, issued together, one per lens. Reviewers must not edit anything. They return findings in their result.

| Lens | Prompt template |
|---|---|
| Judgment | `references/judgment-reviewer.md` |
| Tooling | `references/tooling-reviewer.md` |
| Divergent | `references/divergent-reviewer.md` |

The templates sit in this skill's `references/` folder. Pass each verbatim, substituting the digest path for `<ABSOLUTE_PATH>` (or the inline digest where marked). If a different model family can be selected for a delegated task, use it for the tooling lens. Model diversity is part of the point.

### 3. Synthesize

One more `delegate_task` runs `references/synthesizer.md` verbatim with each reviewer's full output inlined where marked. It returns an Accepted / Rejected / Backlog list.

### 4. Structural enforcement check

Sanity-check the Accepted list. Any item that a lint rule, script, hook, metadata flag, or runtime check would enforce more reliably than prose moves from Accepted to Backlog. Prose is for judgment calls that mechanisms can't enforce.

### 5. Approval

Show the synthesizer's full Accepted / Rejected / Backlog output and wait for explicit approval. The user picks which rows to apply and may redirect routings. Then continue at "Applying approved edits".

## Applying approved edits

Used by both modes. Skill edits change every future session, so never auto-apply: show the proposals and wait for the user to pick which to apply.

Append Backlog items to the project's `lessons.md` under `## Backlog (from reflect)` with `patch` (or `write_file` if the file doesn't exist). Each item names the pattern, what was hit, and the suggested mechanism.

For each approved Accepted row, follow its Routing exactly:

- Trivial edit to an existing skill (a bullet, a tightened sentence, a stale fact): `skill_manage(action='patch')`.
- Substantive edit (a new section, a pattern table, more than ~10 lines): follow `hermes-agent-skill-authoring`, show the draft, then apply with `skill_manage`. In audit mode the drafted file is already in `reports/reflect-<date>/proposed/`.
- `tune description: <skill path>`: rewrite the description to front-load the trigger phrases the user actually used.
- `new skill: <kebab-name>`: `skill_manage(action='create')`, following `hermes-agent-skill-authoring` and the frontmatter of the user's existing skills. Don't invent a shape ad hoc.

If the edited skill is one the user mirrors across tools (the same skill under other agent tools' skill folders), list the matching edit for each mirror copy next to the row, adapted to that copy's frontmatter, paths, and tool names, so the user approves them together. Apply them all, or none.

The skill validator runs on `skill_manage` writes. Fix anything it rejects before declaring done.

Finish with a short list, no preamble:

- Edits applied: `<skill path>`, what changed, one line each.
- New skills created: `<skill path>`, one line each (rare).
- Backlog added to `lessons.md`: one line each.
- Dropped: one line per rejected finding, with the reason.

Session mode adapted from pstack `reflect` (github.com/cursor/plugins). Audit mode adapted from skill-doctor in github.com/warpdotdev/common-skills (MIT, Copyright (c) 2026 Denver Technologies, Inc.), see NOTICE-warp-skill-doctor.txt.
