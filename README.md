# tstack

My agent setup — skills, agents, commands, hooks, instruction files and (sanitized) configs —
for the coding agents I run on Windows:

| Folder | Tool | Live location |
|---|---|---|
| `claude/` | Claude Code | `~/.claude` (`skills-synced/` = my skills synced from claude.ai) |
| `codex/` | OpenAI Codex | `~/.codex` |
| `opencode/` | Opencode | `~/.config/opencode` |
| `hermes/` | Hermes | `~/.hermes` |
| `omp/` | omp | `~/.omp/agent` |
| `shared/` | cross-tool | `~/.agents/skills`, `~/AGENTS.md` |

This repo is a **mirror**, not the source of truth: `sync.py` rebuilds each folder from the
live files, so edit skills where the tool reads them and let the sync pick them up.

## What is never published

- Auth files, sessions, history, logs, caches, databases, `.env`, backups (`*.bak*`), drafts, disabled files.
- Values under secret-looking keys (`*key*`, `*token*`, `*secret*`, `auth`, `password`, …) and whole
  `env` / `headers` / `environment` blocks in configs → `<REDACTED>`.
- Email addresses → `<EMAIL>`; names and IDs listed in a private, gitignored redaction map → placeholders.
- Anthropic-authored skills synced from claude.ai (not mine to redistribute).

Before anything is committed, every file is scanned for secret shapes (API keys, GitHub/Slack/AWS/Google
tokens, JWTs, private keys). Any hit aborts the run.

## Usage

```sh
python sync.py           # rebuild + scan (no git)
python sync.py --push    # rebuild + scan + commit + push
python -m unittest discover -s tests
```

A Windows scheduled task (`tstack-sync`, Sundays 09:00) runs `run-sync.cmd`, which calls
`sync.py --push` and appends to `.private/sync.log`.

## Restoring on a new machine

Copy a folder back to its live location (table above), then refill the `<REDACTED>` values and
`<PLACEHOLDER>`s with your own keys and IDs. Paths assume `C:\Users\<you>`.
