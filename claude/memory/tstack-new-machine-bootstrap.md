---
name: tstack-new-machine-bootstrap
description: "tstack (~/Downloads/tstack, public TukuCorp/tstack) is the new-laptop bootstrap — bootstrap.ps1 + restore.py; noctty and herdr configs are mirrored there too"
metadata:
  node_type: memory
  type: project
  originSessionId: 19e7b9f4-1f3f-4664-b70b-d3f9df2aabbf
  modified: 2026-10-22T20:06:05.832Z
---

Since 2026-10-23, tstack is both the mirror of the agent setup and the new-machine bootstrap: `bootstrap.ps1` (winget → official installers → npm/bun/uv from `machine/packages.json` → `restore.py` → herdr plugins) and `restore.py` (reverse of sync.py). noctty (`%LOCALAPPDATA%/noctty/config.ghostty`, `~/.config/noctty`) and herdr (`%APPDATA%/herdr/config.toml`, plugins) are mirrored.

**Why:** the user wants one clone + one command to make a fresh work laptop feel identical.

**How to apply:** when adding a new tool or config the user relies on, add it to `SOURCES` in sync.py (and the winget/installer list in bootstrap.ps1) so it survives a machine move. Keep noctty assets (shaders, backgrounds) under `~/.config/noctty`, not elsewhere. `python restore.py --dry-run` on this machine must report 0 writes; anything else is a round-trip bug. Related: [[cross-tool-skill-mirrors]], [[global-agent-rules-locations]].
