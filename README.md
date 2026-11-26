# tstack

My agent setup — skills, agents, commands, hooks, instruction files and (sanitized) configs —
for the coding agents I run on Windows, plus the Herdr app (herdr-app + herdr-core `hc`) they run in
and the noctty terminal config. `bootstrap.ps1` rebuilds the whole setup on a new machine.

| Folder | Tool | Live location |
|---|---|---|
| `claude/` | Claude Code | `~/.claude` (`skills-synced/` = my skills synced from claude.ai) |
| `codex/` | OpenAI Codex | `~/.codex` |
| `opencode/` | Opencode | `~/.config/opencode` |
| `hermes/` | Hermes | `~/.hermes`, the disk-cleanup cron script (`live-scripts/`) + workflow skills from `%LOCALAPPDATA%/hermes/skills` (software-development, opencode, research, engineering, gloop, unslop) |
| `agy/` | Antigravity CLI | `~/.gemini/GEMINI.md`, `~/.gemini/config/skills`, `~/.gemini/config/mcp_config.json`, `~/.gemini/config/skills.json` |
| `shared/` | cross-tool | `~/AGENTS.md` |
| `noctty/` | noctty terminal | `%LOCALAPPDATA%/noctty/config.ghostty` + `~/.config/noctty` (`dotconfig/`: shaders, backgrounds) |
| `ahk/` | AutoHotkey v2 | `~/.config/ahk/herdr-toggle.ahk`: Home hides/shows the Herdr app window (terminals keep running in herdr-core); bootstrap adds a Startup shortcut |
| `herdr/` | Herdr app | `app/`: `~/.config/herdr-app/keys.json` + `settings.json` (the app regenerates its AGENTS.md, built-in mods and themes on start) |
| `machine/` | global CLIs, shell | `packages.json`: npm / bun / uv tools installed globally; `powershell/`: Windows PowerShell `$PROFILE` (`codex` proxy wrapper, `claude-code-mode` launcher for experimental Code Mode) |

**Each harness is self-contained** (since 2026-11-24): it loads and runs only files in its own
folders. The shared `~/.agents/skills` pool is retired, every harness has its own skill copies with
its own self-paths, Opencode runs with `OPENCODE_DISABLE_CLAUDE_CODE=1` (user env var) so it ignores
`~/.claude`, and `tests/test_self_contained.py` fails on any rule or skill that points into another
harness (orchestration skills such as necro, coop and reflect are exempt by name).
`grill-with-ui` (vendored, skipped by sync) is a git clone at `~/.claude/skills/grill-with-ui` with
plain copies in the other harnesses; on a new machine, clone it there and copy it.

**agy (Antigravity CLI)** is a full peer since 2026-11-23: `agy/GEMINI.md` holds every Codex section
verbatim (self-paths aside) plus the Claude Code workflow sections (a test enforces it), `agy/skills`
holds all its skills (`agy/skills.json` adds no extra folders), and `agy/mcp_config.json` registers browse (officecli and powerpoint disabled).
Sign in once on a new machine;
`agy/settings.json` carries the default model (Gemini 4 Neon Medium) without `trustedWorkspaces`.

This repo is a **mirror**, not the source of truth: `sync.py` rebuilds each folder from the
live files, so edit skills where the tool reads them and let the sync pick them up.

## What is never published

- Auth files, sessions, history, logs, caches, databases, `.env`, backups (`*.bak*`), drafts, disabled files.
- Values under secret-looking keys (`*key*`, `*token*`, `*secret*`, `auth`, `password`, …) and whole
  `env` / `headers` / `environment` blocks in configs → `<REDACTED>`.
- Email addresses → `<EMAIL>`; names and IDs listed in a private, gitignored redaction map → placeholders.
- The Windows username in paths → `C:\Users\<USER>` (restored to the new machine's username).
- Anthropic-authored skills synced from claude.ai (not mine to redistribute).
- Agent memory (Claude, Codex, Hermes): it names clients and accounts, so it lives in the private wiki repo.

Before anything is committed, every file is scanned for secret shapes (API keys, GitHub/Slack/AWS/Google
tokens, JWTs, private keys). Any hit aborts the run.

## Usage

```sh
python sync.py           # rebuild + scan (no git)
python sync.py --push    # rebuild + scan + commit + push
python restore.py --dry-run   # what restoring onto this machine would change
python -m unittest discover -s tests
```

A Windows scheduled task (`tstack-sync`, Sundays 09:00) runs `run-sync.cmd`, which calls
`sync.py --push` and appends to `.private/sync.log`.

## New machine

```powershell
winget install --id Git.Git -e
git clone https://github.com/TukuCorp/tstack; cd tstack
powershell -ExecutionPolicy Bypass -File bootstrap.ps1 -DryRun   # see what it would do
powershell -ExecutionPolicy Bypass -File bootstrap.ps1
```

`bootstrap.ps1` skips anything already installed, so it is safe to re-run:

1. **winget**: Git, GitHub CLI, Node LTS, Python, uv, Bun, noctty, AutoHotkey v2, JetBrainsMono Nerd Font,
   Helium (the daily browser; browse and Claude in Chrome run in it, Chrome stays as fallback).
2. **Agent CLIs** via each project's official installer: Claude Code, Codex, the Herdr app (which adds herdr-core), Hermes, agy.
3. **Global packages** from `machine/packages.json` (npm, bun, uv tools).
4. **Configs** via `restore.py` (below).
5. **Home toggle** for the Herdr app window (AutoHotkey Startup shortcut), then agent-browser's Chrome
   for headless browsing.
6. **Wiki**: clones the private `TukuCorp/wiki` to `~/wiki` once `gh` is signed in, restores the
   Claude/Codex/Hermes memory stores from it when they are empty, and registers its daily `wiki-sync` task.

Then sign in to each tool and fill the values `restore.py` listed.

Hermes cron jobs are not mirrored (they hold client details). The one tied to a mirrored script is
the weekly disk cleanup (`hermes/live-scripts/disk-cleanup.py`: deterministic safe clean, then a
Herdr app space (a hidden hc terminal when the window is closed) with a file-tools-only Hermes agent on `deepseek-v4.1-flash` that ranks what's left).
Recreate it with:
`hermes cron create "0 10 * * 0" --name "Weekly Disk Cleanup (Sunday)" --no-agent --script disk-cleanup.py --deliver origin --catch-up on`

`restore.py` (`--dry-run` to preview) is the reverse of `sync.py`: every file goes back to the path
it came from, `<USER>` becomes the current username, and a live file it changes is backed up as
`*.bak-tstack-<timestamp>`. Files that still hold placeholders it can't reverse (`<REDACTED>`,
`<EMAIL>`) only fill gaps: an existing live copy always wins, and newly written ones are listed for
you to fill in. Copy `.private/redactions.json` over from the old machine first and its
placeholders are reversed too. Run on the machine it came from, `restore.py` changes nothing.
