# Herdr commands for /coop

`herdr --help` and `herdr agent` / `herdr pane` (no subcommand) print the installed syntax and win if this sheet disagrees. Commands print JSON; read ids from `.result...`. Errors are JSON on stderr with exit status 1.

## Who and where you are

```bash
test "${HERDR_ENV:-}" = 1 || echo "not in herdr"
printf '%s %s %s\n' "$HERDR_WORKSPACE_ID" "$HERDR_TAB_ID" "$HERDR_PANE_ID"
herdr pane get "$HERDR_PANE_ID"     # .result.pane.agent must be claude or agy (you)
herdr pane layout --pane "$HERDR_PANE_ID"   # .result.layout.area.width decides right vs down
```

PowerShell: `$env:HERDR_ENV`, `$env:HERDR_PANE_ID`, `$env:HERDR_TAB_ID`.

A shell that outlived its pane can hold a stale `HERDR_PANE_ID`. If `pane get` fails or names another agent, find your row in `herdr agent list` (your kind + cwd) and use its `pane_id`.

## Reuse or start the peer

```bash
herdr agent get coop-agy            # or coop-claude; reuse only if .result.agent.tab_id == $HERDR_TAB_ID

# split your pane, keep focus with the user; returns .result.pane.pane_id
herdr pane split --pane "$HERDR_PANE_ID" --direction right --cwd "<root>" --no-focus

# driver is Claude Code -> peer is agy
herdr agent start coop-agy --kind agy --pane <new-pane-id> --timeout 120000 -- --dangerously-skip-permissions

# driver is agy -> peer is Claude Code
herdr agent start coop-claude --kind claude --pane <new-pane-id> --timeout 120000 -- --dangerously-skip-permissions

herdr agent read <peer> --source visible --lines 15   # header shows the model; confirm it is the default
```

Never pass `--model` / `-m`: each side runs its own default (agy: `~/.gemini/antigravity-cli/settings.json`; Claude: its configured default).

Start gotchas:

- `agent start` returns `agent_not_ready` (blocked) when the peer shows a first-run screen. Read the pane and handle it:
  - agy "Auto is now the default agent mode ... esc to dismiss" banner: harmless; prompts still go through. Send `esc` only if a prompt sits unsubmitted.
  - Claude "Do you trust the files in this folder?": confirm the folder is `<root>`, then `herdr agent send-keys coop-claude enter`.
  - An update menu: send `escape`; never pick "update now" unasked.
- Run `agent start` directly from your shell, not from inside a launcher script (starts made from scripts have left tabs with no agent).
- The first prompt right after `agent start` can fail with `agent_prompt_stalled` while agy still shows its startup banner (seen 2026-11-24); the input stays empty, so send the same prompt again once.
- Pass `--timeout` to every waiting command (`agent start`, `agent wait`, `agent prompt --wait`), never to `agent prompt` without `--wait` (Herdr rejects it).

## Hand off and get the report-back

```bash
herdr agent prompt <peer> "<phase prompt from templates.md>"
```

No `--wait`. The prompt ends with the report-back line, which the peer runs as its last action:

```bash
herdr agent prompt <DRIVER_PANE> 'coop-<peer> done: <phase> r<N> <VERDICT|PASS|ISSUES|BLOCKED> <file>'
```

The message lands in your pane: as a new turn if you are idle, or mid-turn if you are working (Claude Code shows it as a user message during the turn; verified 2026-11-24 with agy as peer). Either way, read the named file before acting.

Avoid `$` and backticks in prompt text: the peer's TUI takes it literally, but a peer that pastes it into PowerShell will expand it.

## Check on the peer (once, not in a loop)

```bash
herdr agent get <peer>                              # .result.agent.agent_status: working | idle | done | blocked | unknown
herdr agent read <peer> --source recent-unwrapped --lines 60
```

`blocked` means an approval or question UI: read it and answer with `agent send-keys` or a prompt. `idle`/`done` with no report-back and no output file: re-prompt once with the same phase prompt, then log a gap.

## Clean up

Only for a peer you started in this run:

```bash
herdr pane close <peer-pane-id>
```

Never close panes, tabs, or workspaces you did not create. Never run `herdr server stop`.
