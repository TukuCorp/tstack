# Fan-out: one option per model, and the judge

In full mode you make one option yourself, and each other model in `--models` makes one, all in parallel. Using different model families matters here: three samples from one model tend to converge on the same layout. CLI help (`hc --help`, `agy --help`, `codex exec --help`, `claude --help`) wins if this sheet disagrees with it.

## Before launching

1. Check quota with `quota-axi`. Drop any model whose provider shows under 20% remaining, say which one you dropped, and make its option yourself on the same axis.
2. Give each option an axis and a name, then write one option brief per model to `.design/<slug>/briefs/<name>.md` using the template below. Generators get the brief, the contract, the references and their own axis. They don't get the rubric or the other options' axes.
3. Point each model at its brief file. Never paste the brief into a command line: quotes, `$` and backticks break in PowerShell and in TUIs.

## Option brief template

```markdown
# Option: <name> (axis: <axis>)
Goal: one self-contained HTML mockup for the brief below, differing from the others on <axis>: <what that means here>.
Why: the user picks between options that genuinely differ, then grafts parts together.
Brief: <brief.md content: goal, audience, surface/size, real content, taste rules that apply, contract incl. patterns to reject>
References: <paths under refs/ and what each contributes>
Constraints: write only .design/<slug>/options/<name>/index.html (inline CSS, no build, no external assets except Google Fonts); real content, never lorem ipsum; works on a 393px phone and 1440px desktop; include the dev-only state toggle (Demo / Empty / One / Many / Long text) from the gates reference; no purple/indigo gradients, no rounded-2xl on everything, no stock three-card grid, no gradient-clipped text, no coloured left-border stripes on cards, no lone italic serif word in a headline, no blurred orbs or grid backgrounds, no status dots, badges or stats that nothing real backs.
Out of scope: other options, the picker, product code.
Check: render the file once at phone and desktop width if you can and fix anything clipped; the driver runs the full gates afterwards.
Report back: <report-back line for this transport, below>
```

## Transport A: hc terminals (when `HC_TERMINAL_ID` is set, as inside the Herdr app)

Your address is `HC_TERMINAL_ID` (for example `t5`); call it `DRIVER` and write its literal value into the briefs, because in each peer's terminal the variable holds the peer's own address. Read your space and tab from your own labels so the peers open as splits beside you:

```bash
read SPACE TAB < <(hc get "$HC_TERMINAL_ID" | jq -r '.labels["herdr.space"] + " " + .labels["herdr.tab"]' | tr -d '\r')
```

Start each other model as your child with its job as the launch prompt (a send to a booting agent can be dropped):

```bash
P="Read .design/<slug>/briefs/<name>.md and do exactly what it says."
L="--label herdr.space=$SPACE --label herdr.tab=$TAB"
hc run --bg --name design-agy    --cwd "<project root>" $L -- agy --dangerously-skip-permissions -i "$P"
hc run --bg --name design-codex  --cwd "<project root>" $L -- codex --no-daemon --dangerously-bypass-approvals-and-sandbox -C "<project root>" "$P"
hc run --bg --name design-claude --cwd "<project root>" $L -- claude --dangerously-skip-permissions "$P"
```

Report-back line for the brief: `hc send <DRIVER> 'design-<model> done: <name> .design/<slug>/options/<name>/index.html'`. Its last action is to run that line.

- If a name is taken (`hc ls` shows it live), add the slug: `design-agy-<slug>`.
- agy takes its first prompt only through `-i` (a bare positional prompt exits with code 2). Codex needs `--no-daemon`, or its commands run outside hc and its report comes from the wrong address.
- A first-run trust screen (`hc get <name>` says `blocked`): read it with `hc read <name> --lines 0`, confirm the folder, then `hc keys <name> enter`.
- Never pass `--model`. Each agent runs on its own default.

Do your own option meanwhile. Don't poll: reports arrive in your input as `<hc from="t9 design-agy">...</hc>`, and hc also tells you unasked when a peer blocks, errors or exits. If a peer goes quiet, check it once with `hc get <name>` and `hc read <name> --lines 30`, or wait with `hc wait <name> --timeout 600`. End only the peers you started (`hc kill <name>; hc rm <name>`), and only after their report-back arrives.

## Transport B: headless CLIs (outside hc)

Start each one as a background process from the project root, logging to the run folder:

```bash
agy -p "Read .design/<slug>/briefs/<name>.md and do exactly what it says." --dangerously-skip-permissions > .design/<slug>/logs/agy.log 2>&1
codex exec --dangerously-bypass-approvals-and-sandbox -C "<project root>" "Read .design/<slug>/briefs/<name>.md and do exactly what it says." > .design/<slug>/logs/codex.log 2>&1
claude -p "Read .design/<slug>/briefs/<name>.md and do exactly what it says." --dangerously-skip-permissions > .design/<slug>/logs/claude.log 2>&1
```

Use your harness's background mechanism for the launch (a background shell job, not a sleep loop). The report-back line for this transport is "none: the file is the report". The process exiting means it is done. Then check that `options/<name>/index.html` exists. If it is missing, read the log, re-run that model once, and after that make the option yourself and say so.

## Judge (full mode)

For each option, a model that did not make it scores it against the rubric in `brief.md`. Use the same transport, with a judge brief at `.design/<slug>/briefs/judge-<model>.md`:

```markdown
# Judge
Goal: score each listed option against the rubric; you did not make these.
Rubric: <3-6 criteria from brief.md>
Options: <paths to index.html and their gate PNGs>
For each option and criterion give a score 1-5 and one line of evidence pointing at something visible (a region, a state, a PNG). No overall winner, no rewrite.
Write JSON to .design/<slug>/scores-<model>.json: {"<option>": {"<criterion>": {"score": n, "evidence": "..."}}}
Report back: <line>
```

Use one judge when the options came from two models, and two judges when there were three or more makers, so that no option is scored only by its maker. Merge the judges' files into `scores.json` by averaging each criterion. Keep every evidence line. The picker shows the scores. They inform the user's choice and never make it.
