---
name: reflect
description: Review the current session with three parallel reviewer subagents, surface durable learnings, and route each to a concrete edit on an existing skill (or a backlog entry in lessons.md). Use when the user explicitly says "reflect" or "/reflect", typically at the end of a session that involved corrections or friction.
---

# Reflect

Mine the current session for durable learnings, then route them into skill edits.

## When to invoke

Invoke only when the user says "reflect" or "/reflect". Skip when the session is trivial, off-topic, or already covered by an existing skill that was followed correctly. One-offs are not learnings. If the user gave a focus, pass it to every reviewer.

## Process

### 1. Build a session digest

Raw rollouts can be large, so reviewers read a compact digest, never the raw file.

Session rollouts live in `~/.codex/sessions/YYYY/MM/DD/rollout-*.jsonl`. The first line (`type: session_meta`) records the session's `cwd`. Consider only rollouts whose `cwd` matches the current workspace; other rollouts hold private sessions from unrelated projects. The active session is normally the most recently modified matching rollout. Confirm by searching it for a distinctive phrase from this session's opening request, then extract the digest to a temp file:

```bash
jq -r 'select(.type=="response_item") | .payload as $p
  | if $p.type=="message" then ($p.content // [])[] | select(.text) | "\($p.role): \(.text[0:2000])"
    elif ($p.type=="custom_tool_call" or $p.type=="function_call") then "assistant TOOL \($p.name): \(($p.input // $p.arguments // "")|tostring|.[0:300])"
    elif ($p.type|test("_output$")) then "  RESULT: \(($p.output // "")|tostring|.[0:300])"
    else empty end' <rollout>.jsonl > <tmp>/reflect-digest.txt
```

If no rollout matches, write a tight digest of the session yourself (requests, corrections, decisions, tool failures, skills used) and pass that instead. Also read the project's `lessons.md` if one exists, so reviewers don't resurface lessons already recorded.

### 2. Spawn three reviewers in parallel

Start three read-only subagents at once, one per lens. Prefer a different model family for the tooling lens (for example the `ocx-gpt-6-sol` agent if it is defined in `~/.codex/agents/`); the other two use the default agent. Reviewers must not edit anything. They return findings in their final message.

| Lens | Prompt template |
|---|---|
| Judgment | `references/judgment-reviewer.md` |
| Tooling | `references/tooling-reviewer.md` |
| Divergent | `references/divergent-reviewer.md` |

The templates sit next to this skill in `~/.codex/skills/reflect/references/`. Pass each verbatim, substituting the digest path for `<ABSOLUTE_PATH>` (or the inline digest where marked). If subagents are unavailable, run the three lenses yourself in sequence, keeping each lens's output separate.

### 3. Synthesize

One more subagent (or yourself, if subagents are unavailable) runs `references/synthesizer.md` verbatim with each reviewer's full output inlined where marked. It returns an Accepted / Rejected / Backlog list.

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
