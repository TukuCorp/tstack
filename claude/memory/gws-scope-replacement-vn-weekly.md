---
name: gws-scope-replacement-vn-weekly
description: gws auth login REPLACES the whole scope grant, silently breaking the VN Weekly Workplan job's Sheets write
metadata:
  type: project
---

`gws auth login` replaces the entire stored OAuth grant rather than adding to it.
Re-running it with a narrow `--services`/`--scopes` set silently drops every scope
not named, and the only symptom is `403 Request had insufficient authentication
scopes` from whichever API lost access.

This broke the VN Weekly Workplan scheduled task: a login on 2026-09-18 left only
`gmail.modify` + identity scopes, so Phase 2 could not write the sheet on 2026-09-20.
Re-authorized 2026-09-21 with spreadsheets + gmail.modify + identity.

**Why:** the job needs `spreadsheets` (Phase 2 writes the workplan sheet via `gws`)
AND `gmail.modify` (`notify.py` sends the run summary). Phase 1 reads Gmail/Drive
through MCP connectors, not `gws`, so no Drive scope is required.

**How to apply:** always re-auth with the full set, never a subset --
`gws auth login --scopes "https://www.googleapis.com/auth/spreadsheets,https://www.googleapis.com/auth/gmail.modify,openid,email,profile"`.
The flow needs a browser; run it in the background so the localhost callback
listener stays alive, then hand the printed URL to the user. Verify with a real API
call, not `gws auth status` alone. See [[vn-weekly-job-false-ok-reporting]].
