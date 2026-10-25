# tstack

My agent setup — skills, agents, commands, hooks, instruction files and (sanitized) configs —
for the coding agents I run on Windows, plus the terminal (noctty) and multiplexer (herdr) they
run in. `bootstrap.ps1` rebuilds the whole setup on a new machine.

| Folder | Tool | Live location |
|---|---|---|
| `claude/` | Claude Code | `~/.claude` (`skills-synced/` = my skills synced from claude.ai) |
| `codex/` | OpenAI Codex | `~/.codex` |
| `opencode/` | Opencode | `~/.config/opencode` |
| `hermes/` | Hermes | `~/.hermes` + workflow skills from `%LOCALAPPDATA%/hermes/skills` (software-development, opencode, research, engineering, gloop, unslop) |
| `omp/` | omp | `~/.omp/agent` |
| `shared/` | cross-tool | `~/.agents/skills`, `~/AGENTS.md` |
| `noctty/` | noctty terminal | `%LOCALAPPDATA%/noctty/config.ghostty` + `~/.config/noctty` (`dotconfig/`: shaders, backgrounds) |
| `herdr/` | herdr multiplexer | `%APPDATA%/herdr/config.toml`; `plugins.json` = GitHub plugins to reinstall; `local-plugins.json` + `local-plugins/*.patch` = patched clones in `~/.herdr/local-plugins` (upstream commit + my diff); `bin/` = `herdr-html` helper from `~/.local/bin` |
| `machine/` | global CLIs | `packages.json`: npm / bun / uv tools installed globally |

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

1. **winget**: Git, GitHub CLI, Node LTS, Python, uv, Bun, noctty, JetBrainsMono Nerd Font.
2. **Agent CLIs** via each project's official installer: Claude Code, Codex, herdr, Hermes.
3. **Global packages** from `machine/packages.json` (npm, bun → omp, uv tools).
4. **Configs** via `restore.py` (below).
5. **herdr plugins** from `herdr/plugins.json`, pinned to the mirrored commit; then the patched local
   plugins from `herdr/local-plugins.json` (clone at the commit, `git apply` the patch, `herdr plugin link`)
   and agent-browser's Chrome for the herdr browser pane.
6. **Wiki**: clones the private `TukuCorp/wiki` to `~/wiki` once `gh` is signed in, restores the
   Claude/Codex/Hermes memory stores from it when they are empty, and registers its daily `wiki-sync` task.

Then sign in to each tool and fill the values `restore.py` listed.

`restore.py` (`--dry-run` to preview) is the reverse of `sync.py`: every file goes back to the path
it came from, `<USER>` becomes the current username, and a live file it changes is backed up as
`*.bak-tstack-<timestamp>`. Files that still hold placeholders it can't reverse (`<REDACTED>`,
`<EMAIL>`) only fill gaps: an existing live copy always wins, and newly written ones are listed for
you to fill in. Copy `.private/redactions.json` over from the old machine first and its
placeholders are reversed too. Run on the machine it came from, `restore.py` changes nothing.
