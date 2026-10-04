---
name: notebooklm-cli-preference
description: "User wants NotebookLM interactions driven via the nlm CLI directly, not the mcp__notebooklm__* MCP tools"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: a1463832-8ee8-47b7-bde6-ac73265d508c
  modified: 2026-07-30T05:50:50.828Z
---

For NotebookLM work, use the `nlm` CLI (`C:\Users\tukum\.local\bin\nlm.exe`) directly via Bash/PowerShell. The `mcp__notebooklm__*` MCP tools are gone — the server was deregistered on 2026-07-30 (see [[notebooklm-mcp-setup]]), which made this preference the permanent state rather than just a rule.

**Why:** user explicitly said "forget about mcp, only use cli going forward" (2026-07-10 session) after I offered to drive NotebookLM via MCP tools instead of shelling out.

**How to apply:** Any future NotebookLM task (query notebooks, add sources, generate audio/reports/quizzes, research, etc.) should go through `nlm` CLI commands. See [[notebooklm-mcp-setup]] for install/auth details and the `--ai` flag for full command reference.
