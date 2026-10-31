---
name: agent-desktop
description: "See and operate native desktop apps (click buttons, fill fields, read UI state, menus, windows, clipboard, notifications) on this Windows machine through the OS accessibility tree with the agent-desktop CLI. Use for any desktop GUI task on an app without an API. Not for web pages in Chrome (use chrome-devtools-axi) or live PowerPoint/Excel (use the PowerPoint MCP, xlwings or officecli)."
version: 1.0.0
author: tukum (TukuCorp)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [desktop, computer-use, accessibility, gui-automation]
    related_skills: []
---

# agent-desktop

`agent-desktop` (npm global) is a CLI, not an agent: every command prints one JSON envelope (`ok`, `data` or `error`) and the observe, act, verify loop runs in you.

## Rules
- Use `agent-desktop` to see and operate native desktop apps through the OS accessibility tree. Before the first use in a session, run `agent-desktop skills get desktop` and `agent-desktop skills get platform`, and follow them.
- Stay headless (the default): never pass `--headed` unless I allow physical input for that task, because it moves my cursor and takes focus while I am using the machine.
- For live PowerPoint or Excel, prefer the PowerPoint MCP, xlwings or officecli; use agent-desktop for apps without an API.
- UWP apps hosted by ApplicationFrameHost (Calculator) expose only their title bar; report that instead of retrying.
- In PowerShell, quote every ref (`'@s8f3k2p9:e1'`).

