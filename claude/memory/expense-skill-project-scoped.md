---
name: expense-skill-project-scoped
description: The expense skill moved from global to Downloads/remote/expense/.claude/skills/expense on 2026-10-21; only Claude Code (and Opencode via .claude/skills) can see it there
metadata:
  node_type: memory
  type: project
  originSessionId: ce3c5c59-ab72-478c-8d58-ca332285783d
  modified: 2026-10-20T20:40:15.768Z
---

The `expense` skill (Tung's monthly Allotrope Vietnam reimbursement: Gmail label -> Drive -> Sheet -> draft, never send) now lives only at `C:\Users\<USER>\Downloads\remote\expense\.claude\skills\expense\SKILL.md`. Global copies were deleted from `~/.claude/skills`, `~/.agents/skills`, `~/.config/opencode/skills` and Hermes `skills/productivity`, and tstack was synced (commit 76acbd6).

**Why:** user asked to make it project specific. `.claude/` is gitignored in the `remote` repo (remote-data), so the skill, which holds the Drive folder ID and recipient emails, is not pushed.

**How to apply:** run the skill from the expense folder. Codex and Hermes cannot see it (neither reads `.claude/skills` in a project); Hermes skill `gws-workflows/references/cron-run-artifact-verification.md` still mentions a dedicated `expense` skill. On 2026-10-21 the skill gained Git Bash quoting, attachment-ID, cygpath, UTF-8 and ask-about-late-invoices notes from the 2026-10-19 run. Open questions left for the user: whether <SUPERVISOR> is dropped from To/greeting by default, the small-Grab-bill exclusion threshold, and whether the HoldForBatch label is an invoice source. See [[global-agent-rules-locations]] for the other harness paths.
