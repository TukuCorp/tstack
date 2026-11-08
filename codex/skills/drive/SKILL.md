---
name: drive
description: "Automate Google Workspace (Drive, Gmail, Calendar, Sheets, Docs) and NotebookLM using two CLIs: `gws` (Google Workspace CLI) and `nlm` (NotebookLM CLI). Use for Drive file operations, Gmail search or sending, Calendar events, Sheets read/write, Docs creation, NotebookLM notebooks, adding sources, audio overviews, or querying notebooks. Supports two accounts: work (`<EMAIL>`) and personal (`<EMAIL>`)."
---

# Google Workspace + NotebookLM — Drive Skill

Two CLI tools are available on this machine:

| Tool | Purpose | Install |
|------|---------|---------|
| `gws` | Google Workspace: Drive, Gmail, Calendar, Sheets, Docs | `npm install -g @googleworkspace/cli` |
| `nlm` | NotebookLM: notebooks, sources, chat, audio overviews | `uv tool install notebooklm-mcp-cli` |

---

## Account Configuration

| Account | Email | gws | nlm profile |
|---------|-------|-----|-------------|
| Work (default) | <EMAIL> | bare `gws` (store `~/.config/gws`; leave `GOOGLE_WORKSPACE_CLI_CONFIG_DIR` unset) | `--profile work` |
| Personal | <EMAIL> | see `~/wiki/wiki/gws-cli.md` (Testing-mode token, expires after 7 days) | `--profile personal` |

For Allotrope work, use bare `gws` without asking. `~/.config/gws-work` and `~/.config/gws-personal` hold no credentials: never point `GOOGLE_WORKSPACE_CLI_CONFIG_DIR` at them.

---

## Current Local Notes

Chrome's persisted `Preferences.account_info` order is not the same thing as Google's live `authuser` routing order. For browser automation, use the live Google routing below.

Current live Google app routing for this machine:

| Google account | `authuser` / `u/` index |
|----------------|--------------------------|
| `<EMAIL>` | `0` |
| `<EMAIL>` | `1` |
| `<EMAIL>` | `2` |

When a task uses browser control via Playwright MCP extension mode, always route to the requested account explicitly:

- Personal (`<EMAIL>`): use index `0`
- Work (`<EMAIL>`): use index `1`
- `<EMAIL>`: use index `2`
- Never infer Google `authuser` routing from Chrome `account_info` ordering
- Gmail: `https://mail.google.com/mail/u/<index>/#inbox`
- Drive: `https://drive.google.com/drive/u/<index>/home`
- NotebookLM and most other Google apps: add `?authuser=<index>` or `&authuser=<index>`
- After navigation, verify the resulting page title or visible account matches the requested account and correct if needed

gws syntax and auth:

- `gws <service> <resource> <method> --params '<json>'` (plus `--json '<body>'` for request bodies, `-o PATH` for binary downloads). There are no `--query`, `--max-results` or `--fields` flags; put `q`, `pageSize`, `fields` inside `--params`.
- `gws schema <service.resource.method>` shows the exact parameter shape.
- On Windows PowerShell, inline JSON quoting breaks. Build the JSON with Python `json.dumps` and call gws through `subprocess`, or run gws from Git Bash. More Windows quirks: `~/wiki/wiki/gws-cli.md`.
- Check auth with a real call (`gws drive files list --params '{"pageSize":1}'`), not `gws auth status`. Never run `gws auth login` unasked: it replaces the whole scope grant.
- `nlm` uses `--profile` on subcommands, for example `nlm notebook list --profile work`; check with `nlm login --check --profile work`.

---

## gws — Google Workspace CLI

All output is JSON. Examples (bash quoting):

```bash
# Drive: search, metadata (check trashed/parents before trusting a same-named file), download
gws drive files list --params '{"q":"name contains '\''Q1'\'' and trashed=false","pageSize":20,"fields":"files(id,name,mimeType,webViewLink,parents)"}'
gws drive files get --params '{"fileId":"FILE_ID","fields":"id,name,webViewLink,parents,trashed,modifiedTime"}'
gws drive files get --params '{"fileId":"FILE_ID","alt":"media"}' -o ./local.pdf

# Gmail: search, read, draft (raw = base64url RFC 822 message)
gws gmail users messages list --params '{"userId":"me","q":"is:unread from:partner@example.com","maxResults":20}'
gws gmail users messages get --params '{"userId":"me","id":"MESSAGE_ID","format":"full"}'
gws gmail users drafts create --params '{"userId":"me"}' --json '{"message":{"raw":"BASE64URL"}}'

# Calendar
gws calendar events list --params '{"calendarId":"primary","timeMin":"2026-05-01T00:00:00Z","timeMax":"2026-05-31T23:59:59Z","singleEvents":true,"orderBy":"startTime"}'

# Sheets
gws sheets spreadsheets values get --params '{"spreadsheetId":"SHEET_ID","range":"Sheet1!A1:Z100"}'
```

Drive query syntax: `name contains 'text'` | `mimeType = 'application/pdf'` | `'FOLDER_ID' in parents` | `fullText contains 'keyword'` | `modifiedTime > '2026-01-01T00:00:00'` | `trashed = false`. Gmail `q` mirrors the Gmail search bar.

---

## nlm — NotebookLM CLI

The installed CLI accepts `--profile` on the subcommand itself:

```bash
nlm notebook list --profile work
nlm notebook list --profile personal
```

### Notebooks

```bash
# List all notebooks
nlm --profile work notebook list

# Create notebook
nlm --profile work notebook create "Research Topic"

# Get details
nlm --profile work notebook get NOTEBOOK_ID

# Rename / delete
nlm --profile work notebook rename NOTEBOOK_ID "New Title"
nlm --profile work notebook delete NOTEBOOK_ID
```

### Sources

```bash
# Add URL source
nlm --profile work source add NOTEBOOK_ID --url "https://example.com/article"

# Add local file (PDF, DOCX, TXT, etc.)
nlm --profile work source add NOTEBOOK_ID --file ./report.pdf

# Add Google Drive file by ID
nlm --profile work source add NOTEBOOK_ID --drive "DRIVE_FILE_ID"

# Add YouTube video
nlm --profile work source add NOTEBOOK_ID --url "https://www.youtube.com/watch?v=VIDEO_ID"

# Add plain text
nlm --profile work source add NOTEBOOK_ID --text "Paste content here"

# List / remove sources
nlm --profile work source list NOTEBOOK_ID
nlm --profile work source remove NOTEBOOK_ID SOURCE_ID
```

### Chat / Query

```bash
# Ask a question
nlm --profile work chat NOTEBOOK_ID "What are the key risks?"
nlm --profile work chat NOTEBOOK_ID "Summarize the main findings"

# Continue a thread
nlm --profile work chat NOTEBOOK_ID "Follow up" --thread THREAD_ID

# List threads
nlm --profile work chat list NOTEBOOK_ID
```

### Audio Overview

```bash
# Generate (async, 2–5 min)
nlm --profile work audio create NOTEBOOK_ID
nlm --profile work audio create NOTEBOOK_ID --focus "Focus on financial projections"

# Check status
nlm --profile work audio status NOTEBOOK_ID   # pending | processing | completed | failed

# Download
nlm --profile work audio download NOTEBOOK_ID --output ./overview.mp3
```

### Study Guide / Slides

```bash
nlm --profile work slides revise NOTEBOOK_ID   # generates structured outline
nlm --profile work slides get NOTEBOOK_ID
```

---

## Common Workflows

### Research pipeline
```bash
# 1. Create notebook
nlm --profile work notebook create "Vietnam Grid Storage 2026"   # → save NOTEBOOK_ID

# 2. Add sources
nlm --profile work source add NOTEBOOK_ID --url "https://evn.com.vn/report"
nlm --profile work source add NOTEBOOK_ID --file ./analysis.pdf

# 3. Query
nlm --profile work chat NOTEBOOK_ID "What is the storage capacity target?"

# 4. Generate audio overview
nlm --profile work audio create NOTEBOOK_ID
# wait ~3 min...
nlm --profile work audio download NOTEBOOK_ID --output ~/Desktop/overview.mp3
```

---

## Auth Setup (first-time, run once per account)

gws: ask the user first; see `~/wiki/wiki/gws-cli.md` (re-login replaces every scope).

```bash
# nlm — opens browser, authenticate as the correct Google account
nlm login --profile work
nlm login --profile personal
```

**Re-auth:** nlm cookies expire every 2–4 weeks. If any nlm command fails with an auth/session error, run `nlm login --profile <name>` to refresh.

---

## Reference Files

For full flag listings and advanced options, read these files when needed:

- **`references/gws-reference.md`** — older gws reference; its `--query`/config-dir syntax is stale, prefer `gws schema` and `--help`
- **`references/nlm-reference.md`** — complete nlm reference: all notebook/source/chat/audio/slides subcommands, MCP tools table, auth details
