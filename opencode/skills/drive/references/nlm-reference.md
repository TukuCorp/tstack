# nlm — NotebookLM CLI Reference

Full command reference for `notebooklm-mcp-cli` (`nlm`).

Install: `uv tool install notebooklm-mcp-cli`

Multi-account pattern — always pass `--profile`:
```bash
nlm --profile work <command>
nlm --profile personal <command>
```

**Profiles map to accounts:**
- `work` → <EMAIL>
- `personal` → <EMAIL>

---

## Auth

### Login (sets up or refreshes cookies)
```bash
nlm login --profile work      # opens browser, authenticate as work Google account
nlm login --profile personal  # opens browser, authenticate as personal Google account
```

**Cookie expiry:** NotebookLM sessions expire every 2–4 weeks. If any command returns an auth or session error, re-run `nlm login --profile <name>`.

### Check login status
```bash
nlm --profile work notebook list  # if this succeeds, auth is valid
```

### MCP Server Setup (for AI coding agents)
```bash
nlm setup add opencode          # adds nlm as MCP server in OpenCode config
nlm setup remove opencode       # removes from OpenCode
nlm setup list                  # shows current MCP configurations
```

---

## Notebooks

### List all notebooks
```bash
nlm --profile work notebook list
# Returns: array of {id, title, createdAt, updatedAt, sourceCount}
```

### Get notebook details
```bash
nlm --profile work notebook get NOTEBOOK_ID
# Returns: {id, title, sources, audioOverview status, etc.}
```

### Create notebook
```bash
nlm --profile work notebook create "Notebook Title"
# Returns: {id, title, ...} — save the id for subsequent operations
```

### Delete notebook
```bash
nlm --profile work notebook delete NOTEBOOK_ID
```

### Rename notebook
```bash
nlm --profile work notebook rename NOTEBOOK_ID "New Title"
```

---

## Sources

### List sources in a notebook
```bash
nlm --profile work source list NOTEBOOK_ID
# Returns: array of {id, title, type, url, createdAt}
```

### Add source — URL
```bash
nlm --profile work source add NOTEBOOK_ID --url "https://example.com/article"
nlm --profile work source add NOTEBOOK_ID --url "https://arxiv.org/abs/2401.00001"
```

### Add source — local file (PDF, DOCX, TXT, etc.)
```bash
nlm --profile work source add NOTEBOOK_ID --file ./report.pdf
nlm --profile work source add NOTEBOOK_ID --file ./notes.txt
```

### Add source — Google Drive file
```bash
nlm --profile work source add NOTEBOOK_ID --drive "GOOGLE_DRIVE_FILE_ID"
# Use the Drive file's ID (from URL or gws drive files list)
```

### Add source — YouTube video
```bash
nlm --profile work source add NOTEBOOK_ID --url "https://www.youtube.com/watch?v=VIDEO_ID"
```

### Add source — plain text
```bash
nlm --profile work source add NOTEBOOK_ID --text "Paste content here..."
```

### Remove source
```bash
nlm --profile work source remove NOTEBOOK_ID SOURCE_ID
```

---

## Chat / Query

### Ask a question against a notebook
```bash
nlm --profile work chat NOTEBOOK_ID "What are the key investment risks?"
nlm --profile work chat NOTEBOOK_ID "Summarize the main findings"
nlm --profile work chat NOTEBOOK_ID "What does the data say about tariff changes?"
```

Returns a grounded answer with citations from the notebook's sources.

### Continue a conversation (thread)
```bash
nlm --profile work chat NOTEBOOK_ID "Follow up question" --thread THREAD_ID
```

### List chat threads
```bash
nlm --profile work chat list NOTEBOOK_ID
```

---

## Audio Overview

Audio overviews are AI-generated podcast-style discussions of the notebook content.

### Create audio overview
```bash
nlm --profile work audio create NOTEBOOK_ID
# Initiates generation — async, takes a few minutes
```

### Check generation status
```bash
nlm --profile work audio status NOTEBOOK_ID
# Returns: pending | processing | completed | failed
```

### Download audio overview
```bash
nlm --profile work audio download NOTEBOOK_ID --output ./overview.mp3
```

### Customise audio overview (focus area)
```bash
nlm --profile work audio create NOTEBOOK_ID --focus "Focus on the financial projections and risks"
```

---

## Slides / Study Guide

### Generate study guide / slides
```bash
nlm --profile work slides revise NOTEBOOK_ID
# Generates a structured slide outline from notebook content
```

### Get existing slides
```bash
nlm --profile work slides get NOTEBOOK_ID
```

---

## Notes

### List notes in notebook
```bash
nlm --profile work note list NOTEBOOK_ID
```

### Create note
```bash
nlm --profile work note create NOTEBOOK_ID "Note content here..."
```

### Get note
```bash
nlm --profile work note get NOTEBOOK_ID NOTE_ID
```

---

## MCP Tools (35 available via `nlm setup add opencode`)

When the MCP server is enabled in OpenCode, all 35 nlm tools are available directly without running shell commands. Key tools:

| Tool | Purpose |
|------|---------|
| `list_notebooks` | List all notebooks for a profile |
| `get_notebook` | Get notebook details |
| `create_notebook` | Create new notebook |
| `add_source_url` | Add URL source |
| `add_source_file` | Add file source |
| `add_source_drive` | Add Drive file source |
| `list_sources` | List sources in notebook |
| `remove_source` | Remove a source |
| `chat` | Query notebook with a question |
| `create_audio_overview` | Start audio generation |
| `get_audio_status` | Check audio progress |
| `download_audio` | Download finished audio |
| `revise_slides` | Generate study guide |
| `create_note` | Add a note to notebook |
| `list_notes` | List notebook notes |

---

## Common Workflows

### Research pipeline: add sources → chat → audio
```bash
# 1. Create notebook for a topic
nlm --profile work notebook create "Vietnam Energy Market 2026"
# → save NOTEBOOK_ID from output

# 2. Add sources
nlm --profile work source add NOTEBOOK_ID --url "https://evn.com.vn/annual-report"
nlm --profile work source add NOTEBOOK_ID --file ./market-analysis.pdf
nlm --profile work source add NOTEBOOK_ID --drive "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs"

# 3. Ask questions
nlm --profile work chat NOTEBOOK_ID "What is the current storage capacity target?"
nlm --profile work chat NOTEBOOK_ID "What are the main regulatory risks?"

# 4. Generate audio overview for commute listening
nlm --profile work audio create NOTEBOOK_ID
# wait a few minutes...
nlm --profile work audio status NOTEBOOK_ID
nlm --profile work audio download NOTEBOOK_ID --output ~/Desktop/vietnam-energy-overview.mp3
```

### Find and query existing notebook
```bash
# List to find the notebook
nlm --profile work notebook list

# Query it
nlm --profile work chat "NOTEBOOK_ID_FROM_LIST" "Your question here"
```

---

## Tips

- Notebook IDs are UUIDs — copy from `notebook list` output
- Source addition is async for large files; `source list` will show processing status
- Audio generation typically takes 2–5 minutes depending on notebook size
- The `--profile` flag must come immediately after `nlm`, before the subcommand
- If auth fails, always try `nlm login --profile <name>` first before debugging further
- NotebookLM supports PDFs up to ~500 pages; split large documents if needed
