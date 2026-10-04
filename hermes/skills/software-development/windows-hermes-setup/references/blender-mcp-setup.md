# Blender MCP Setup (ahujasid/blender-mcp)

Installation + configuration of [BlenderMCP](https://github.com/ahujasid/blender-mcp) on
Windows under Hermes/Claude Code. Records the uv isolation workaround, addon install
path, and Claude config needed when the Hermes venv's `mcp` package conflicts.

## Components

| Component | Description | Location |
|-----------|-------------|----------|
| **Blender Addon** | Socket server inside Blender (listens on port 9876) | Blender's scripts/addons/ dir |
| **MCP Server** | Python package (`uvx blender-mcp`) bridges MCP ↔ Blender socket | Managed by uv |
| **Claude Config** | Declares the MCP server so Claude Code loads Blender tools | `.claude/mcp.json` or global `~/.claude.json` |

## Setup Steps

### 1. Install the Blender Addon

Download `addon.py` from the blender-mcp repo into Blender's addons directory:

```bash
BLENDER_VERSION="4.1"
BLENDER_PATH="/c/Users/tukum/Blender/blender-4.1.1-windows-x64"
ADDONS="$BLENDER_PATH/$BLENDER_VERSION/scripts/addons"
curl -sL -o "$ADDONS/blender_mcp_addon.py" \
  "https://raw.githubusercontent.com/ahujasid/blender-mcp/main/addon.py"
```

Then **enable once in Blender GUI** (one-time):
- Open Blender → Edit → Preferences → Add-ons
- Search "Blender MCP" or locate `blender_mcp_addon.py`
- Check the box — the addon auto-starts a socket server on port 9876

The addon **refuses to start** in background mode (`blender -b`). Blender must run
with a GUI (or under a virtual display such as `xvfb-run` on Linux).

### 2. Configure the MCP Server

`uvx blender-mcp` manages the server Python process. From a clean terminal:

```bash
PYTHONPATH="" uvx --python 3.11 blender-mcp
```

The `PYTHONPATH=""` is **required** when running inside a Hermes environment — see
"uv isolation workaround" below.

### 3. Add Claude Code Config

**Project-level** (`.claude/mcp.json` in the repo):

```json
{
  "mcpServers": {
    "blender": {
      "command": "uvx",
      "args": ["--python", "3.11", "blender-mcp"],
      "env": {
        "PYTHONPATH": "",
        "DISABLE_TELEMETRY": "true",
        "UV_PYTHON_PREFERENCE": "only-managed"
      }
    }
  }
}
```

**Or global** via Claude CLI:

```bash
claude mcp add blender uvx blender-mcp
```

Then manually add the `env` block to `~/.claude.json` under the project's
`mcpServers.blender.env`:

```json
{
  "PYTHONPATH": "",
  "DISABLE_TELEMETRY": "true",
  "UV_PYTHON_PREFERENCE": "only-managed"
}
```

## uv Isolation Workaround

### Symptom

Running `uvx blender-mcp` from a terminal where the Hermes venv `mcp` package is
on `sys.path` produces import errors:

```
File "...\\hermes-agent\\venv\\Lib\\site-packages\\mcp\\__init__.py", line 1
  from .client.session import ClientSession
```

The import picks up the wrong `mcp` package (the one from Hermes' venv) instead of
the one bundled with blender-mcp's uv-managed environment.

### Root cause

`uvx` inherits the parent shell's `sys.path`, which includes the Hermes venv's
site-packages. Both Hermes and blender-mcp use a package named `mcp` (the MCP
protocol SDK), and Python's import resolution finds the Hermes one first.

### Fix

Clear `PYTHONPATH` before launching — this prevents uv from discovering packages
outside its own managed environment:

```bash
PYTHONPATH="" uvx blender-mcp
```

If the Hermes process environment itself leaks `PYTHONPATH`, use a wrapper `.cmd`
script:

```batch
@echo off
setlocal
set PYTHONPATH=
uvx blender-mcp %*
```

### Detection

The `--refresh` flag alone does NOT fix this — `uvx --refresh blender-mcp` still
inherits the wrong path. The env var must be cleared at the shell level.

## Environment Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `BLENDER_HOST` | `localhost` | Host for the Blender socket server |
| `BLENDER_PORT` | `9876` | Port for the Blender socket server |
| `DISABLE_TELEMETRY` | unset | Set `true` to opt out of anonymous usage data |

## Workflow

1. **Start Blender** — open Blender GUI. The addon auto-starts the socket server
   on port 9876 (visible in the 3D View sidebar → BlenderMCP tab).
2. **Launch Claude Code** — `claude` in the project directory. Claude auto-loads
   the Blender MCP tools (hammer icon in the tool list).
3. **Interact** — ask Claude to create/modify objects, apply materials, set up
   lighting, render, etc.

## Troubleshooting

| Problem | Likely cause | Fix |
|---------|-------------|-----|
| `uvx blender-mcp` fails with Hermes `mcp` import error | PYTHONPATH leak | Set `PYTHONPATH=""` in env |
| `spawn uvx ENOENT` | Client doesn't inherit terminal PATH | Use full path to `uvx.exe`, or wrap with `cmd /c uvx blender-mcp` |
| Blender refuses to start as GUI | Headless server / CI | Run with a virtual display (`xvfb-run`) or run actual Blender GUI locally |
| Connect button stays disconnected | Blender not running | Open Blender first, verify addon is enabled and the tab shows "Connected" |
| First command fails, subsequent work | Cold-start timing | Re-send the command — the server warms up after the first request |
