# Handing the rewrite to agy

hc (herdr-core) runs the terminals behind the Herdr app. `hc --skill` and `hc <command> --help` print the installed syntax and win if this sheet disagrees. Piped output is JSON.

## Find or start agy in your tab

```bash
echo "$HC_TERMINAL_ID"     # empty = not in hc: do the rewrite yourself
hc get "$HC_TERMINAL_ID" | jq -r '.labels["herdr.space"] + " " + .labels["herdr.tab"]' | tr -d '\r'   # SPACE TAB
hc ls                      # reuse a live agy row (coop-agy, unslop-agy) whose hc get shows your TAB in labels["herdr.tab"]
```

If there is none, write the draft first (below) and start agy as your child in a split beside you, on its default model (never pass `--model`), with the job as its launch prompt:

```bash
hc run --bg --name unslop-agy --cwd "$PWD" --label herdr.space=<SPACE> --label herdr.tab=<TAB> -- \
  agy --dangerously-skip-permissions -i "<prompt>"
```

agy takes its first prompt only through `-i`; a bare positional prompt exits with code 2. A folder agy hasn't seen shows a trust screen (`hc get unslop-agy` says `blocked`): read it with `hc read unslop-agy --lines 0`, confirm the folder, `hc keys unslop-agy enter`. The "Auto is now the default agent mode" banner is harmless.

## Send the job and wait

Write the draft to `<dir>/<name>.draft.md` (the scratchpad, or next to the deliverable). Avoid `$` and backticks in the prompt text. Use the prompt as the launch prompt above, or send it to a reused agent with `hc send <agent> "<prompt>"`. Then wait without polling:

```bash
hc wait <agent> --timeout 600
```

Prompt:

```
Use your unslop skill on <dir>/<name>.draft.md and write only the cleaned text to <dir>/<name>.clean.md.
Brief: audience <...>; house voice <...>; keep these terms as they are: <...>; structure fixes: <...>.
Keep every fact, number, date, name, link, quote, code span, citation and footnote marker exactly. Add no facts.
Keep the format (Markdown, email, slide lines) and roughly the length unless the brief says cut.
When done, reply with the single word DONE.
```

`hc wait` returns when agy stops working, blocks or exits (`reason: timeout` is a check-in: wait again). Then check that `<name>.clean.md` exists. If agy is `blocked`, read its screen and answer it. If the file is missing, send the prompt once more, then fall back to doing the rewrite yourself.

## Afterwards

Run `fact_guard.py` on the two files, fix any drift, then do the mechanical check. Leave a reused agent running. End an agent you started (`hc kill unslop-agy; hc rm unslop-agy`) when the whole task is done, not after each rewrite, so later rewrites in the same task reuse it.
