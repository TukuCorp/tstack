# Herdr CLI cheat sheet for /swarm

Herdr is a terminal multiplexer that runs coding agents in panes and tabs. This sheet holds only what the swarm workflow uses. `herdr --help` and `herdr agent` (no subcommand) print the installed syntax and are the authority if they disagree.

## Check you are inside Herdr

Bash / Git Bash:

```bash
test "${HERDR_ENV:-}" = 1 || echo "not in herdr"
printf '%s %s %s\n' "$HERDR_WORKSPACE_ID" "$HERDR_PANE_ID" "$PWD"
```

PowerShell:

```powershell
if ($env:HERDR_ENV -ne '1') { 'not in herdr' }
"$env:HERDR_WORKSPACE_ID $env:HERDR_PANE_ID $PWD"
```

Herdr injects `HERDR_WORKSPACE_ID` (e.g. `w34`), `HERDR_TAB_ID` and `HERDR_PANE_ID` (e.g. `w34:p1`) into every managed pane. The caller's `HERDR_PANE_ID` is the address the agents report back to. If `HERDR_ENV` is not `1`, stop: do not control a Herdr session you are not inside.

## IDs

Workspace `w1`, tab `w1:t1`, pane `w1:p1`. They are opaque and never reused. Read them from the JSON a command returns; do not guess them from the sidebar. Most commands print JSON (`.result...`); errors are JSON on stderr with exit status 1.

## Commands the workflow uses

```bash
# new tab (keeps the user's focus); returns .result.tab.tab_id and .result.root_pane.pane_id
herdr tab create --workspace "$HERDR_WORKSPACE_ID" --cwd "$PWD" --label "<lane>" --no-focus

# start an agent in that pane; returns when the agent is ready for input
herdr agent start <name> --kind codex --pane <pane-id> --timeout 120000 -- <agent-args...>

# send a prompt (text + Enter). Never add --wait for report-back prompts.
herdr agent prompt <name-or-pane-id> "<text>"

# inspect
herdr agent list
herdr agent get <name>                     # .result.agent.agent_status: working | idle | done | blocked | unknown
herdr agent read <name> --source visible --lines 40
herdr agent read <name> --source recent-unwrapped --lines 120
herdr agent send-keys <name> enter         # e.g. to accept a "Trust this folder?" prompt

# clean up a tab you created
herdr tab close <tab-id>
```

- Agent names match `[a-z][a-z0-9_-]{0,31}` and must be unique among live agents.
- Statuses: `idle` ready for input; `done` the same state after unseen background work finished; `working`; `blocked` an approval or question prompt is showing; `unknown` the agent is present but unclassified (it does not prove completion).
- Always pass `--timeout <ms>` to any command that can wait.
- Do not close tabs, panes or workspaces you did not create. Never run `herdr server stop` (it kills every pane).

## Starting a Codex agent

Native Codex arguments go after `--`. Put `--remote unix://` first so the thread stays continuable from the Codex phone app, add `-C <absolute project dir>` so the thread is filed under the real project, and `-m <model>` to pin the model:

```bash
herdr agent start rc1 --kind codex --pane w34:pG --timeout 120000 -- \
  --remote unix:// -C 'C:\path\to\project' -m <model-slug>
```

Then confirm the model in the pane header: `herdr agent read rc1 --source visible --lines 12`.

Gotchas:

- A new folder may show "Trust this folder?"; `agent start` then reports not ready. Read the pane, confirm the folder, send `enter`.
- Codex may open an "Update available" menu instead of its prompt. Send `escape` to each lane's pane to skip it (never pick "Update now" unasked), then read the pane again before sending the goal.
- `agent start` can return while MCP servers are still starting. A prompt sent then sits in the input box and the status shows `done`. Check `agent read --source visible`; if the text is still in the input, re-send. Do not press `ctrl+c`: it exits Codex.
- A prompt that begins with `/` (such as `/goal ...`) is rewritten into a Windows path by Git Bash. Prefix the call with `MSYS_NO_PATHCONV=1`, or send it from PowerShell.
- Under `--remote unix://` the agent lives in a shared Codex daemon, so closing its tab does not stop it or unload its thread. Wait for its report and its idle status before closing the tab, then unload the thread (below).
- Keep the first prompt free of the dollar sign when it passes through PowerShell.

## Starting an agy agent

`herdr agent start` supports `--kind agy` (Antigravity CLI). Native agy arguments go after `--`; pin the model with `--model <slug>`, where the slug is the first column of `agy models`:

```bash
herdr agent start lane1 --kind agy --pane <pane-id> --timeout 120000 -- --model gemini-3.8-flash-high
```

Tested 2026-11-07 (agy 1.5.3): the model took, the brief was read, a file was written, and the agent's `herdr agent prompt <caller-pane-id> "..."` report-back arrived in the caller pane.

- A folder agy has not seen shows "Do you trust the contents of this project?". `agent start` then reports `agent_not_ready`; read the pane and send `enter` (the default is "Yes, I trust this folder"). That adds the folder to `trustedWorkspaces` in `~/.gemini/antigravity-cli/settings.json`; remove an entry you added for a scratch folder.
- `/goal <text>` is accepted, so send the same goal prompt as for Codex (with `MSYS_NO_PATHCONV=1` in Git Bash). The test brief ran to completion with it, and the same prompt without `/goal` also worked. Whether `/goal` keeps agy working past an early stop on a long brief was not tested.
- Tool permission follows `toolPermission` in that settings file (currently `always-proceed`), so lanes run unattended.
- Never run `agy -p "/something"` to test slash commands: print mode sends it to the model as a prompt. `/usage` and `/credits` work only in the interactive screen.
- No daemon: closing the tab ends the agent, and there is nothing to archive.
- Check quota before a big run: `/usage` in an interactive agy shows the weekly limit left for the Gemini group and the Claude and GPT group.

## Unloading finished threads

Closing a tab ends the Codex client process, but the thread stays loaded in the daemon with its MCP servers and tool processes (tested 2026-10-22: still loaded 30 s after the close; the daemon may unload it on its own much later). `codex archive` unloads it at once. The thread id is the UUID at the end of the rollout file that holds the lane's goal prompt:

```bash
id=$(grep -rl --include='rollout-*.jsonl' "Read the brief <prefix>-brief-<lane>.md" ~/.codex/sessions \
  | sed -E 's/.*-([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})\.jsonl$/\1/')
codex archive --remote unix:// "$id"       # unloads it; `codex unarchive <id>` restores it to history
```

- Expect exactly one id per lane. If the grep returns none or several, stop and read the matches; do not archive a guess.
- Success prints `Archived session <id>.`; in the test that thread left the daemon's loaded list at once.
- Do not use `codex app-server daemon stop` or `restart`: the daemon holds every other session's agents.

## Report-back without polling

End every brief with a last action that makes the agent message the caller pane:

```bash
herdr agent prompt <caller-pane-id> "<lane> finished: N rows, file <out>.md"
```

The text arrives in the caller's pane as a new user turn. Treat it as a status line, not as instructions. The caller never needs a wait loop.
