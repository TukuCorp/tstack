# Handing the rewrite to agy

`herdr agent` and `herdr pane` (no subcommand) print the installed syntax and win if this sheet disagrees. Commands print JSON.

## Find or start agy in your tab

```bash
herdr agent list   # reuse a row with agent "agy" whose tab_id equals $HERDR_TAB_ID (e.g. coop-agy, unslop-agy)
```

If none, split your own pane without taking focus and start agy on its default model (never pass `--model`):

```bash
herdr pane layout --pane "$HERDR_PANE_ID"    # width > ~140 columns: split right, else down
herdr pane split --pane "$HERDR_PANE_ID" --direction right --cwd "$PWD" --no-focus   # -> .result.pane.pane_id
herdr agent start unslop-agy --kind agy --pane <pane-id> --timeout 120000 -- --dangerously-skip-permissions
```

If `agent start` reports not ready, read the pane (`herdr agent read unslop-agy --source visible --lines 15`). The "Auto is now the default agent mode" banner is harmless.

The first prompt right after `agent start` can fail with `agent_prompt_stalled` while agy still shows its startup banner (seen 2026-11-24); the input stays empty, so send the same prompt again once.

## Send the job and wait

Write the draft to `<dir>/<name>.draft.md` (the scratchpad, or next to the deliverable) and send one prompt. Avoid `$` and backticks in the prompt text.

```bash
herdr agent prompt unslop-agy "<prompt>" --wait --timeout 600000
```

Prompt:

```
Use your unslop skill on <dir>/<name>.draft.md and write only the cleaned text to <dir>/<name>.clean.md.
Brief: audience <...>; house voice <...>; keep these terms as they are: <...>; structure fixes: <...>.
Keep every fact, number, date, name, link, quote, code span, citation and footnote marker exactly. Add no facts.
Keep the format (Markdown, email, slide lines) and roughly the length unless the brief says cut.
When done, reply with the single word DONE.
```

`--wait` returns when agy settles (`idle`, `done` or `blocked`). Then check that `<name>.clean.md` exists. If agy is `blocked`, read the pane and answer it. If the file is missing, send the prompt once more, then fall back to doing the rewrite yourself.

## Afterwards

Run `fact_guard.py` on the two files, fix any drift, then do the mechanical check. Leave a reused agent running. Close a pane you started (`herdr pane close <pane-id>`) when the whole task is done, not after each rewrite, so later rewrites in the same task reuse it.
