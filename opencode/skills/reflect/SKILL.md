---
name: reflect
description: This skill should be used when the user explicitly invokes `/reflect` or says "reflect". Reviews the current session with three parallel reviewer subagents, surfaces durable learnings, and routes each to a concrete edit on an existing skill (or a backlog entry in lessons.md).
argument-hint: "[optional focus, e.g. 'the deploy mistakes']"
---

# Reflect

Mine the current session for durable learnings, then route them into skill edits.

## When to invoke

Invoke only when the user says "reflect" or "/reflect". Skip when the session is trivial, off-topic, or already covered by an existing skill that was followed correctly. One-offs are not learnings. If the user gave a focus, pass it to every reviewer.

## Process

### 1. Build a session digest

Write a tight digest of this session to a temp file, `reflect-digest.txt`, one line per event: `user: <request or correction>`, `assistant: <decision or claim>`, `assistant TOOL <name>: <key arguments>`, `RESULT: <outcome or error>`. Cover every user correction, every decision and its stated reason, every tool failure and retry, and every skill or agent that was used. Quote corrections verbatim. Keep it under ~60 KB.

Also read the project's `lessons.md` if one exists, so reviewers don't resurface lessons already recorded.

### 2. Spawn three reviewers in parallel

One message, three Task tool calls using the `general` subagent. Reviewers must not edit anything. They return findings in their response.

| Lens | Prompt template |
|---|---|
| Judgment | `references/judgment-reviewer.md` |
| Tooling | `references/tooling-reviewer.md` |
| Divergent | `references/divergent-reviewer.md` |

The templates sit next to this skill in `~/.config/opencode/skills/reflect/references/`. Pass each verbatim, substituting the digest path for `<ABSOLUTE_PATH>` (or the inline digest where marked). If a reviewer agent on a different model family is configured, use it for the tooling lens. Model diversity is part of the point.

### 3. Synthesize

One more `general` Task call runs `references/synthesizer.md` verbatim with each reviewer's full output inlined where marked. It returns an Accepted / Rejected / Backlog list.

### 4. Structural enforcement check

Sanity-check the Accepted list. Any item that a lint rule, script, hook, metadata flag, or runtime check would enforce more reliably than prose moves from Accepted to Backlog. Prose is for judgment calls that mechanisms can't enforce.

### 5. Apply, only with approval

Show the synthesizer's full Accepted / Rejected / Backlog output and wait for explicit approval. The user picks which rows to apply and may redirect routings. Skill edits change every future session, so never auto-apply.

Append Backlog items to the project's `lessons.md` under `## Backlog (from reflect)`, creating the file if needed. Each item names the pattern, what was hit, and the suggested mechanism.

For each approved Accepted row, follow its Routing exactly:

- Trivial edit to an existing skill (a bullet, a tightened sentence, a stale fact): edit it directly.
- Substantive edit (a new section, a pattern table, more than ~10 lines): use the `skill-creator` skill if available, otherwise draft the change, show the diff, then apply.
- `tune description: <skill path>`: rewrite the description to front-load the trigger phrases the user actually used.
- `new skill via create-skill: <kebab-name>`: create it with `skill-creator`, matching the frontmatter conventions of the user's existing skills. Don't invent a shape ad hoc.

After editing, parse-check the YAML frontmatter of every touched `SKILL.md`.

### 6. Summarize for the user

Short list, no preamble:

- Edits applied: `<skill path>`, what changed, one line each.
- New skills created: `<skill path>`, one line each (rare).
- Backlog added to `lessons.md`: one line each.
- Dropped: one line per rejected finding, with the synthesizer's reason.

<!-- Adapted from pstack `reflect` by Lauren Tan (MIT), github.com/cursor/plugins @ 12d587d. -->
