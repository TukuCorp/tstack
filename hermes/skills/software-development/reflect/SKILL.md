---
name: reflect
description: "Review the current session with three parallel reviewer subagents, surface durable learnings, and route each to a concrete edit on an existing skill (or a backlog entry in lessons.md). Use only when the user says \"reflect\" or \"/reflect\"."
version: 1.0.0
author: Lauren Tan (pstack), adapted
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [reflection, learnings, skill-maintenance, review, subagents]
    related_skills: [hermes-agent-skill-authoring]
---

# Reflect

Mine the current session for durable learnings, then route them into skill edits.

## When to invoke

Invoke only when the user says "reflect" or "/reflect". Skip when the session is trivial, off-topic, or already covered by an existing skill that was followed correctly. One-offs are not learnings. If the user gave a focus, pass it to every reviewer.

## Process

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

### 5. Apply, only with approval

Show the synthesizer's full Accepted / Rejected / Backlog output and wait for explicit approval. The user picks which rows to apply and may redirect routings. Skill edits change every future session, so never auto-apply.

Append Backlog items to the project's `lessons.md` under `## Backlog (from reflect)` with `patch` (or `write_file` if the file doesn't exist). Each item names the pattern, what was hit, and the suggested mechanism.

For each approved Accepted row, follow its Routing exactly:

- Trivial edit to an existing skill (a bullet, a tightened sentence, a stale fact): `skill_manage(action='patch')`.
- Substantive edit (a new section, a pattern table, more than ~10 lines): follow `hermes-agent-skill-authoring`, show the draft, then apply with `skill_manage`.
- `tune description: <skill path>`: rewrite the description to front-load the trigger phrases the user actually used.
- `new skill via create-skill: <kebab-name>`: `skill_manage(action='create')`, following `hermes-agent-skill-authoring` and the frontmatter of the user's existing skills. Don't invent a shape ad hoc.

The skill validator runs on `skill_manage` writes. Fix anything it rejects before declaring done.

### 6. Summarize for the user

Short list, no preamble:

- Edits applied: `<skill path>`, what changed, one line each.
- New skills created: `<skill path>`, one line each (rare).
- Backlog added to `lessons.md`: one line each.
- Dropped: one line per rejected finding, with the synthesizer's reason.

Adapted from pstack `reflect` (github.com/cursor/plugins).
