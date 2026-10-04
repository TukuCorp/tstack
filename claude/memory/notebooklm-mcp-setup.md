---
name: notebooklm-mcp-setup
description: "notebooklm-mcp-cli is installed for `nlm` CLI use; its MCP server was deregistered 2026-07-30 for launching Chrome every session, but was RE-ADDED under the new name `notebooklm-mcp` without the headless guard — still registered and leaking as of 2026-08-31"
metadata: 
  node_type: memory
  type: project
  originSessionId: a6b61835-9511-4a8d-9e2f-4b31a8f018f7
  modified: 2026-08-31T05:51:52.948Z
---

`notebooklm-mcp-cli` v0.8.4 (github.com/jacob-bd/notebooklm-mcp-cli) is installed via `uv tool` on this desktop, exposing `nlm` / `notebooklm-mcp` binaries in `~/.local/bin`. Authenticated Chrome profile `default` is logged in as <EMAIL> (also `work` and `personal` profiles exist under `~/.notebooklm-mcp-cli/profiles/`). `default_notebook_id` is not set — no notebook is pinned by default, so calls likely need a notebook specified explicitly.

**REMOVED as an MCP server on 2026-07-30.** It was registered user-scoped as `notebooklm` (2026-07-10) via:
`claude mcp add --scope user notebooklm --env PYTHONUTF8=1 --env PYTHONIOENCODING=utf-8 -- cmd /c "C:\Users\tukum\.local\bin\notebooklm-mcp-server.cmd"`
The entry was deleted from `~/.claude.json` `mcpServers` because **it opened a visible Chrome window on every Claude Code session start**: `NotebookLMFastMCP.start()` awaits `_ensure_client()` *before* serving stdio (`notebooklm_mcp/server.py:247-253`) and `config.headless` defaults to `False` (`config.py:34`), so booting the server eagerly launched Selenium → `chromedriver.exe` → `chrome.exe --user-data-dir=%TEMP%\scoped_dir*` (a fresh temp profile, hence a new *window* rather than a tab). Those processes never got reaped: 22 orphaned chromedrivers and 821 leaked `scoped_dir*` folders (3.9 GB) had accumulated. Remote control made it conspicuous because its daemon/worker sessions each boot their own MCP servers, so 3-4 windows appeared at once. Removal is the right fix, not `NOTEBOOKLM_HEADLESS=true`, because of [[notebooklm-cli-preference]] — the MCP tools were never to be used anyway.

**Windows bug + fix:** the server crashes instantly on startup with `UnicodeEncodeError: 'charmap' codec can't encode character '\U0001f680'` — it prints a 🚀 emoji startup banner via `rich`, and Windows' legacy `cp1252` console encoding can't render it. Fix is forcing UTF-8 I/O via `PYTHONUTF8=1` and `PYTHONIOENCODING=utf-8` env vars on the MCP server process (done above). Without these env vars, `claude mcp get notebooklm` shows "Failed to connect."

**Why:** user asked (2026-04-18 session) to set this up for global CC use; it got installed/authenticated but never registered with a client. Finished registration 2026-07-10.

**RE-ADDED — status as of 2026-08-31 (/doctor scan).** The removal above did not stick: `~/.claude.json` `mcpServers` now contains a *different* user-scope entry named **`notebooklm-mcp`** (not the old `notebooklm`), `command: notebooklm-mcp` → `~/.local/bin/notebooklm-mcp.exe`, with only `PYTHONPATH` in `env` — **no `NOTEBOOKLM_HEADLESS`, and not even the `PYTHONUTF8`/`PYTHONIOENCODING` vars** the Windows bug below requires. Evidence the leak returned, milder than before: **199 `scoped_dir*` folders (47.6 MB) in `%TEMP%`, oldest 2026-08-16, newest stamped at session start on 2026-08-31**; no orphaned `chromedriver.exe` processes were live at scan time, so the reaping is better than the 22-process/3.9 GB state of July. Usage is still zero — 0 `mcp__notebooklm-mcp__*` calls AND 0 `nlm` CLI runs across 50 sessions / 9 days. Disable with `/mcp disable notebooklm-mcp` (per-project — repeat per project); never `claude mcp remove` (it wipes config + OAuth tokens).

**How to apply:** use the `nlm` CLI, not the `mcp__notebooklm-mcp__*` tools, per [[notebooklm-cli-preference]]. Do **not** register or re-enable the MCP server without also setting `NOTEBOOKLM_HEADLESS=true`, or the Chrome-window-per-session bug returns. If it is ever re-added, remember `cmd /c "<path>"` must be run via the **PowerShell tool, not Bash/Git-Bash** — Git Bash's MSYS path translation mangles `/c` into `C:/`.

Also noted: `~/.notebooklm-mcp-cli` is shared across tools — a separate agent (Hermes, using its own bundled `uv.exe` at `C:\Users\tukum\AppData\Local\hermes\bin\uv.exe`) was observed actively running `notebooklm-mcp chat --headless` concurrently against the same profile. See [[cross-tool-skill-mirrors]] for other cross-tool overlap on this machine.
