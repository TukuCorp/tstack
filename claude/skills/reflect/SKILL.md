---
name: reflect
description: Review the current session with three parallel reviewer subagents, surface durable learnings, and route each to a concrete edit on an existing skill (or a backlog entry in lessons.md). Use when the user says "reflect" or "/reflect", typically at the end of a session that involved corrections or friction.
argument-hint: "[optional focus, e.g. 'the deploy mistakes']"
---

# Reflect

Mine the current session for durable learnings, then route them into skill edits.

## When to invoke

Invoke when the user says "reflect" or "/reflect". Skip when the session is trivial, off-topic, or already covered by an existing skill the parent followed correctly. One-offs are not learnings. If the user gave a focus, pass it to every reviewer.

## Process

### 1. Build a session digest

Raw transcripts can run to tens of MB, so reviewers read a compact digest, never the raw file.

Session transcripts live in `~/.claude/projects/<project-slug>/<session-id>.jsonl`, where the slug is the working directory with every non-alphanumeric character replaced by `-` (`C:\Users\me\repo` → `C--Users-me-repo`). Subagent transcripts sit in `<session-id>/subagents/`. Stay inside the current project's folder. Other folders hold private sessions from unrelated projects.

The active session is normally the most recently modified `.jsonl` there. Confirm by grepping it for a distinctive phrase from this session's opening request. Then extract the digest into the scratchpad directory (or a temp dir):

```bash
jq -r 'select(.type=="user" or .type=="assistant") | .type as $t
  | (.message.content | if type=="string" then [{type:"text",text:.}] else (. // []) end)[]
  | if .type=="text" then "\($t): \(.text[0:2000])"
    elif .type=="tool_use" then "\($t) TOOL \(.name): \(.input|tostring|.[0:300])"
    elif .type=="tool_result" then "  RESULT: \((.content|tostring)[0:300])"
    else empty end' <session>.jsonl > <scratch>/reflect-digest.txt
```

If no file matches, write a tight digest of the session yourself (requests, corrections, decisions, tool failures, skills used) and pass that instead. Also read the project's `lessons.md` if one exists, so reviewers don't resurface lessons already recorded.

### 2. Spawn three reviewers in parallel

One message, three Agent tool calls. Reviewers must not edit anything. They return findings in their response.

| Lens | `subagent_type` | Prompt template |
|---|---|---|
| Judgment | `general-purpose` | `references/judgment-reviewer.md` |
| Tooling | `ocx-gpt-6-sol` (different model family on purpose), else `general-purpose` | `references/tooling-reviewer.md` |
| Divergent | `general-purpose` | `references/divergent-reviewer.md` |

Pass each template verbatim, substituting the digest path for `<ABSOLUTE_PATH>` (or the inline digest where marked). If an agent type is unavailable, fall back to `general-purpose` and say so.

### 3. Synthesize

One `general-purpose` Agent call with `references/synthesizer.md` verbatim and each reviewer's full output inlined where marked. It returns an Accepted / Rejected / Backlog list.

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

After editing, parse-check the frontmatter of every touched `SKILL.md` (`claude plugin validate <skills-dir>` works for a whole folder).

### 6. Summarize for the user

Short list, no preamble:

- Edits applied: `<skill path>`, what changed, one line each.
- New skills created: `<skill path>`, one line each (rare).
- Backlog added to `lessons.md`: one line each.
- Dropped: one line per rejected finding, with the synthesizer's reason.

<!-- Adapted from pstack `reflect` by Lauren Tan (MIT), github.com/cursor/plugins @ 12d587d. -->
