# hc commands for /coop

hc (herdr-core) runs every terminal and agent behind the Herdr app. `hc --skill` and `hc <command> --help` print the installed syntax and win if this sheet disagrees. Piped output is JSON; errors are JSON on stderr.

## Who and where you are

```bash
echo "$HC_TERMINAL_ID"                       # your address, e.g. t5 = DRIVER; empty = not in hc, stop
hc get "$HC_TERMINAL_ID" | jq -r '.labels["herdr.space"], .labels["herdr.tab"]'   # SPACE, TAB
```

PowerShell: `$env:HC_TERMINAL_ID`; `$l = (hc get $env:HC_TERMINAL_ID | ConvertFrom-Json).labels; $l.'herdr.space'; $l.'herdr.tab'`.

Strip a trailing `\r` from ids parsed on Windows: a label with one silently misses and the peer lands in a new tab instead of beside you. Write the literal DRIVER address (for example `t5`) into every prompt, never the variable: in the peer's terminal it holds the peer's own address.

## Reuse or start the peer

```bash
hc get coop-agy        # or coop-claude; reuse only if live and .labels["herdr.tab"] equals your TAB
```

To start it, launch it as your child in a split beside you, with the kickoff prompt in the launch command (a send to a booting agent can be dropped):

```bash
# driver is Claude Code -> peer is agy (agy takes its first prompt only through -i)
hc run --bg --name coop-agy --cwd "<root>" --label herdr.space=<SPACE> --label herdr.tab=<TAB> -- \
  agy --dangerously-skip-permissions -i "<kickoff prompt>"

# driver is agy -> peer is Claude Code
hc run --bg --name coop-claude --cwd "<root>" --label herdr.space=<SPACE> --label herdr.tab=<TAB> -- \
  claude --dangerously-skip-permissions "<kickoff prompt>"

hc read <peer> --lines 0      # header shows the model; confirm it is the default
```

Never pass `--model` or `-m`: each side runs its own default (agy: `~/.gemini/antigravity-cli/settings.json`; Claude: its configured default).

Start gotchas:

- `hc get <peer>` shows `blocked` on a first-run screen. Read it and handle it:
  - "Do you trust the contents of this project?" (agy) or "Do you trust the files in this folder?" (Claude): confirm the folder is `<root>`, then `hc keys <peer> enter`. On 2026-11-26 agy ran its launch prompt right after the trust screen.
  - agy "Auto is now the default agent mode ... esc to dismiss" banner: harmless. Send `esc` only if a prompt sits unsubmitted.
  - An update menu: `hc keys <peer> esc`; never pick "update now" unasked.
- agy with a bare positional prompt exits with code 2 ("Prompts are read only from -p/--print, -i/--prompt-interactive"). Use `-i`.
- In Git Bash prefix with `MSYS_NO_PATHCONV=1` if any argument starts with `/`.

## Hand off and get the report-back

```bash
hc send <peer> "<phase prompt from templates.md>"
```

The prompt ends with the report-back line, which the peer runs as its last action:

```bash
hc send <DRIVER> 'coop-<peer> done: <phase> r<N> <VERDICT|PASS|ISSUES|BLOCKED> <file>'
```

It arrives in your input as `<hc from="t9 coop-agy">coop-agy done: ...</hc>`, as a new turn if you are idle or mid-turn if you are working (verified 2026-11-26 with agy and Claude). hc also sends you a note, unasked, when the peer blocks, errors or exits. Either way, read the named file before acting.

Avoid `$` and backticks in prompt text: the peer's TUI takes it literally, but a peer that pastes it into PowerShell will expand it.

## Check on the peer (once, not in a loop)

```bash
hc get <peer>                 # .status: working | idle | done | blocked | error
hc read <peer> --lines 60
```

`blocked` means an approval or question UI: read it and answer with `hc keys` or a send. `idle`/`done` with no report-back and no output file: re-send the same phase prompt once, then log a gap. To wait without polling, `hc wait <peer> --timeout 600` returns when it stops working.

## Clean up

Only for a peer you started in this run: `hc kill <peer>; hc rm <peer>` (closes its pane). The peer is your child, so it also ends when your session ends. Never kill or send to terminals you did not start. Never `hc server stop`.
