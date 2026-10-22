---
name: ppt-mcp-setup
description: "ppt-mcp (live PowerPoint control) install and per-harness MCP config locations, registered 2026-10-20"
metadata:
  node_type: memory
  type: reference
  originSessionId: ce3c5c59-ab72-478c-8d58-ca332285783d
  modified: 2026-10-20T14:11:00.707Z
---

`ppt-mcp` v2.3.0 (github.com/ykuwai/ppt-mcp, 156 tools, live PowerPoint over COM) is installed with `uv tool install ppt-mcp`, binary `C:\Users\<USER>\.local\bin\ppt-mcp.exe`. Update with `uv tool upgrade ppt-mcp`.

Registered as `powerpoint` in all five harnesses on 2026-10-20:
- Claude Code: `claude mcp add --scope user powerpoint -- <exe>` (stored in `~/.claude.json`)
- Codex: `codex mcp add powerpoint -- <exe>` (`~/.codex/config.toml`)
- Opencode: `mcp.powerpoint` in `~/.config/opencode/opencode.json` (type local; shows "pending" until first use). A separate `ppt` entry there is disabled and pre-dates this.
- omp: `~/.omp/agent/mcp.json` (`mcpServers`, stdio). It loads the server but reported only 64 `ppt_` tools in print mode vs 156 on the server; cause not checked.
- Hermes: `hermes mcp add powerpoint --command <exe>` needs a confirmation on stdin; pipe a newline in (`"`n`n" | hermes mcp add ...`) or it exits 255 without saving. Config is `%LOCALAPPDATA%/hermes/config.yaml`.

Usage: open the deck in PowerPoint, then call `ppt_activate_presentation` first so every tool is locked to that file. Uses uv, not npx, so the npm lock bug in [[firecrawl-and-npx-mcp-setup]] doesn't apply.
