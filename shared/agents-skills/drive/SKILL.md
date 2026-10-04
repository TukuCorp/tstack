---
name: drive
description: >
  Automate Google Workspace (Drive, Gmail, Calendar, Sheets, Docs) and NotebookLM
  using two CLIs: gws (Google Workspace CLI) and nlm (NotebookLM CLI).
  Use this skill for any task involving Google Drive file operations, Gmail search
  or sending, Calendar events, Sheets read/write, Docs creation, NotebookLM
  notebooks, adding sources, audio overviews, or querying notebooks.
  Supports two accounts: work (<EMAIL>) and personal (<EMAIL>).
compatibility: opencode
---

# Google Workspace + NotebookLM — Drive Skill

Two CLI tools are available on this machine:

| Tool | Purpose | Install |
|------|---------|---------|
| `gws` | Google Workspace: Drive, Gmail, Calendar, Sheets, Docs | `npm install -g @googleworkspace/cli` |
| `nlm` | NotebookLM: notebooks, sources, chat, audio overviews | `uv tool install notebooklm-mcp-cli` |

---

## Account Configuration

| Account | Email | gws env prefix | nlm profile |
|---------|-------|----------------|-------------|
| Work | <EMAIL> | `GOOGLE_WORKSPACE_CLI_CONFIG_DIR=~/.config/gws-work` | `--profile work` |
| Personal | <EMAIL> | `GOOGLE_WORKSPACE_CLI_CONFIG_DIR=~/.config/gws-personal` | `--profile personal` |

Always confirm with the user which account to use before running a command, unless context makes it obvious.

---

## Current Local Notes

Chrome's persisted `Preferences.account_info` order is not the same thing as Google's live `authuser` routing order. For browser automation, use the live Google routing below.

Current live Google app routing for this machine:

| Google account | `authuser` / `u/` index |
|----------------|--------------------------|
| `<EMAIL>` | `0` |
| `<EMAIL>` | `1` |
| `<EMAIL>` | `2` |

When a task uses browser control via the built-in `playwright_browser_*` or `browser_*` tools, always route to the requested account explicitly:

- Personal (`<EMAIL>`): use index `0`
- Work (`<EMAIL>`): use index `1`
- `<EMAIL>`: use index `2`
- Never infer Google `authuser` routing from Chrome `account_info` ordering
- Gmail: `https://mail.google.com/mail/u/<index>/#inbox`
- Drive: `https://drive.google.com/drive/u/<index>/home`
- NotebookLM and most other Google apps: add `?authuser=<index>` or `&authuser=<index>`
- After navigation, verify the resulting page title or visible account matches the requested account and correct if needed

The installed CLIs on this machine differ slightly from some older examples below:

- `gws` uses `gws <service> <resource> <method> --params '<json>'`
- Prefer `gws schema <service.resource.method>` to inspect the exact parameter shape before running an unfamiliar command
- `nlm` uses `--profile` on subcommands, for example `nlm notebook list --profile work`
- Before CLI work, verify auth first:

```powershell
$env:GOOGLE_WORKSPACE_CLI_CONFIG_DIR = "$HOME/.config/gws-work"
gws auth status

nlm login --check --profile work
```

If auth is missing or expired, re-authenticate before continuing.

---

## gws — Google Workspace CLI

Every gws command must be prefixed with the account's config dir. Define helpers to keep commands readable:

```bash
alias gws-work='GOOGLE_WORKSPACE_CLI_CONFIG_DIR=~/.config/gws-work gws'
alias gws-personal='GOOGLE_WORKSPACE_CLI_CONFIG_DIR=~/.config/gws-personal gws'
```

All output is JSON. Pipe to `| jq` or `| python -m json.tool` to inspect.

### Drive — common operations

```bash
# Search files
gws-work drive files list --query "name contains 'Q1'" --fields "files(id,name,mimeType,webViewLink)"

# Upload
gws-work drive +upload ./report.pdf --parent-id FOLDER_ID --name "Report.pdf"

# Download
gws-work drive files download FILE_ID --output ./local.pdf

# Get metadata (incl. shareable link)
gws-work drive files get FILE_ID --fields "id,name,webViewLink,parents,modifiedTime"

# Create folder
gws-work drive files +create-folder "Folder Name" --parent-id PARENT_ID

# Copy / move
gws-work drive files copy FILE_ID --name "Copy" --parent-id FOLDER_ID
gws-work drive files update FILE_ID --add-parents NEW_ID --remove-parents OLD_ID
```

Drive query syntax: `name contains 'text'` | `mimeType = 'application/pdf'` | `'FOLDER_ID' in parents` | `fullText contains 'keyword'` | `modifiedTime > '2026-01-01T00:00:00'` | `trashed = false`

### Gmail — common operations

```bash
# Search messages
gws-work gmail messages list --query "is:unread from:partner@example.com" --max-results 20

# Read message
gws-work gmail messages get MESSAGE_ID --format full

# Send email
gws-work gmail +send --to "recipient@example.com" --subject "Subject" --body "Body" --attachment ./file.pdf

# Create draft
gws-work gmail drafts +create --to "r@example.com" --subject "Draft" --body "Body"
```

Gmail query syntax mirrors the Gmail search bar: `is:unread`, `from:`, `to:`, `subject:`, `has:attachment`, `after:2026/01/01`, `label:inbox`

### Calendar — common operations

```bash
# Next 7 days
gws-work calendar +agenda --days 7

# List events in range
gws-work calendar events list --calendar-id primary \
  --time-min "2026-05-01T00:00:00Z" --time-max "2026-05-31T23:59:59Z" \
  --single-events --order-by startTime

# Create event
gws-work calendar +create "Board Call" \
  --start "2026-05-05T10:00:00" --end "2026-05-05T11:00:00" \
  --attendees "a@example.com,b@example.com" \
  --description "Agenda" --location "Zoom"

# List calendars
gws-work calendar calendar-list list
```

### Sheets — common operations

```bash
# Create
gws-work sheets spreadsheets create --title "My Spreadsheet"

# Read range
gws-work sheets values get SHEET_ID --range "Sheet1!A1:Z100"

# Write / update
gws-work sheets values +update SHEET_ID \
  --range "Sheet1!A1" \
  --values '[["Header1","Header2"],["val1","val2"]]' \
  --value-input-option USER_ENTERED

# Append rows
gws-work sheets values +append SHEET_ID \
  --range "Sheet1!A1" \
  --values '[["new","row"]]' \
  --value-input-option USER_ENTERED
```

### Docs — common operations

```bash
# Create document
gws-work docs documents +create --title "Meeting Notes"

# Get document content
gws-work docs documents get DOC_ID

# Insert text
gws-work docs documents batch-update DOC_ID \
  --requests '[{"insertText":{"location":{"index":1},"text":"Hello World\n"}}]'
```

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

### Find a Drive file and get its share link
```bash
gws-work drive files list --query "name contains 'Q1 Report' and trashed=false" \
  --fields "files(id,name,webViewLink)"
# → extract webViewLink from JSON output
```

### Send email with attachment
```bash
gws-work gmail +send \
  --to "partner@example.com" \
  --subject "Q1 Update" \
  --body "Please find attached." \
  --attachment ./Q1-Report.pdf
```

---

## Auth Setup (first-time, run once per account)

```bash
# gws — opens browser OAuth flow
GOOGLE_WORKSPACE_CLI_CONFIG_DIR=~/.config/gws-work gws auth setup
GOOGLE_WORKSPACE_CLI_CONFIG_DIR=~/.config/gws-personal gws auth setup

# nlm — opens browser, authenticate as the correct Google account
nlm login --profile work
nlm login --profile personal
```

**Re-auth:** nlm cookies expire every 2–4 weeks. If any nlm command fails with an auth/session error, run `nlm login --profile <name>` to refresh.

---

## Reference Files

For full flag listings and advanced options, read these files when needed:

- **`references/gws-reference.md`** — complete gws reference: all Drive/Gmail/Calendar/Sheets/Docs subcommands, flags, query syntax, field selectors, pagination
- **`references/nlm-reference.md`** — complete nlm reference: all notebook/source/chat/audio/slides subcommands, MCP tools table, auth details
