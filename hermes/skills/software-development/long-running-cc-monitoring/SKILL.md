---
name: long-running-cc-monitoring
description: Workflow for monitoring long-running Claude Code sessions in background PTY — avoid going dark, catch blocking questions, report promptly.
---

# Long-Running Claude Code Monitoring

Use when you submit a multi-step task to Claude Code via background PTY (e.g. "fix all issues then commit and push") that may take minutes and/or ask blocking questions.

## 1. Start with a `todo` reminder

After submitting the prompt, immediately set a todo item to re-check:

```json
todo(todos=[{id:"cc-check-1", content:"Check Claude Code progress — re-poll process log", status:"in_progress"}])
```

## 2. Poll for progress

The right polling cadence depends on how CC was launched:

### tmux sessions (fast polling, 10-15s)

When CC runs inside tmux, `tmux capture-pane` is a lightweight read that doesn't disturb CC's TUI. Poll every 10-15 seconds:

- `tmux capture-pane -t <session> -p -S -5` for the tail of output
- `tmux capture-pane -t <session> -p -S -15` for a broader view
- Key signals to watch for:
  - Has output stopped changing for 30+ seconds → check if it's waiting for input
  - Look for ❯ prompt followed by a question (not a command echo)
  - "esc to interrupt" + ❯ with empty text = waiting for your answer

### Background PTY sessions (slower polling, 60-90s)

When CC runs via `terminal(background=true, pty=true)`, each `process(action="log")` call is heavier and may interfere with the TUI rendering. Poll less frequently:

- `process(action='poll')` for quick status
- `process(action='log')` for full output every 2-3 polls
- Same signal detection rules as tmux sessions (look for ❯ + question text)

## 3. Answer blocking questions immediately

If Claude asks a question (text after `❯` that isn't a previous command echo), answer it. Common patterns:
- "can you double check X" → say yes/no or give direction
- "should I proceed with Y" → answer
- "X failed, what should I do" → guide it

## 4. Use notify_on_complete where possible

For pure-execution steps (test runs, commits, pushes), consider splitting them into a separate `terminal(background=true, pty=true, notify_on_complete=true)` call so you get pinged when they finish.

## 5. Watch for session limits

Claude Code accounts have rate/session limits that vary by plan tier (Pro, Max, Team). Output like:
```
You've hit your session limit · resets 5:20pm (Asia/Saigon)
```
means all processing has stopped until the reset time. The process is blocked and will not recover on its own.

**Detection:** The log shows this message with no activity indicators following. The output stops changing.

**Mitigation:**
- Split very long multi-phase tasks across separate sessions (e.g., Gmail scanning in one session, Sheet updates in another after the reset)
- Use `--max-budget-usd` to proactively cap spend before hitting the limit
- Check the reset time and plan accordingly — if the task is time-sensitive, reduce model effort (`--effort low`) or scope to fit within the available budget

## 5a. Orchestrator-side iteration budget (Hermes cron agents)

Distinct from CC's own session limit. The **Hermes agent doing the monitoring** also has a per-run tool-call cap. This bites cron-driven orchestration hardest because each `tmux capture-pane`, `send-keys`, `read_file`, etc. costs one iteration from the same budget.

See `references/hermes-iteration-budget.md` for the full investigation notes — where the cap comes from, which knob actually controls it for cron jobs, the polling budget math, and the env-var trap to avoid.

**Default cap:** `60` tool calls per cron agent run (`HERMES_MAX_ITERATIONS=60` env var injected into the Hermes runtime).

**The error:** `You've reached the maximum number of tool-calling iterations allowed.` — the agent stops mid-task before verification / close-out. CC may still be alive in tmux, but the orchestrator can no longer answer picker questions, verify side effects, or write the summary file.

**The actual knob (in priority order, see `references/hermes-iteration-budget.md`):**

1. `config.yaml → agent.max_turns` — cron jobs read this directly. `HERMES_MAX_ITERATIONS` env var is **ignored** by the cron runner.
2. CLI arg `--max-turns N` — wins over config when explicitly set.
3. Subagents: `config.yaml → delegation.max_iterations` (default 50).

**The fix for the CC Pipeline pattern (and any long-running-monitor job):**

```bash
hermes config set agent.max_turns 150
```

This is global (affects all cron jobs), but the trade-off is favorable: the other cron jobs use 5-15 calls, so a 150 ceiling is non-binding for them. The monitoring-heavy jobs get the headroom they need.

**Polling budget math (rule of thumb):** with `max_turns=150` and ~15 setup/verification calls, you get ~135 polls of headroom. That's 45-60 minutes at 30-45s polling — enough to monitor a full brainstorm + plan + execution cycle.

**Pitfall — env var trap:** setting `HERMES_MAX_ITERATIONS` in `.env` or the cron job prompt does **nothing** for cron-spawned agents. The cron runner (`cron/scheduler.py` line ~2800) reads `agent.max_turns` from config and passes it to `AIAgent(max_iterations=...)` directly. The env var only applies to the interactive TUI/CLI session.

**Pitfall — invisible blow-up in low-cadence monitoring:** if polling drifts to 30s and a 6-picker brainstorm takes 9 minutes, you may hit the 60 cap during verification. Symptom: orchestrator truncates with `TASK_DONE: failed` or "iteration budget reached" before writing the summary file. CC keeps working but close-out is lost. Either bump `agent.max_turns` or use a `no_agent=true` bash script for monitoring (see section 6 — the script does not consume the agent's iteration budget at all).

## 6. Automated Monitor Script Pattern (Fully Autonomous Runs)

For fully autonomous runs (cron jobs, CI pipelines, or any scenario where you can't watch CC's output continuously), deploy a background bash script alongside the CC tmux session. The script polls aggressively, auto-answers blocking questions with default options, and signals completion when CC produces its expected output artifact.

### Architecture

```
Hermes Agent (cron trigger)
  ├─ terminal: tmux new-session -d -s cc-<project>
  │     └─ send-keys: cd <workdir> && claude --model <model>
  ├─ write_file: .monitor.sh (polling script)
  └─ terminal(background, notify_on_complete): bash .monitor.sh
        ├─ Every 10s: tmux capture-pane → grep for question patterns
        │   └─ If question detected: tmux send-keys Enter (accept default)
        ├─ Every 10s: check for output artifact file existence
        │   └─ If found: break, report
        └─ On completion: tmux kill-session, rm temp files
```

### Monitor Script Template

See `references/auto-monitor-script-template.md` for a reusable bash template. Copy and adapt the following parameters:

- **`SESSION`** — tmux session name (e.g., `cc-cpi`)
- **`COMPLETE_FILE`** — path to the output artifact CC is expected to create
- **`QUESTION_PATTERNS`** — grep patterns for questions CC might ask (default: Continue, Proceed, Allow, Approve, "Enter to confirm", "Switch model", "Yes, switch to")
- **`POLL_INTERVAL`** — seconds between polls (default: 10)
- **`SILENT_THRESHOLD`** — consecutive idle checks before assuming completion (default: 6 = ~60s)

### Key CC Dialogs the Script Must Handle

**Dialog 1: Model-switch confirmation** (`/model` command)
```
Switch model?
Your next response will be slower and use more tokens
❯ 1. Yes, switch to Sonnet 5
  2. No, go back
```
**Detection:** `"Switch model?"` or `"Yes, switch to"` in pane — NOT caught by `AskUserQuestion`, `Recommended`, `picker`, or `(Recommended)` patterns.
**Action:** `tmux send-keys Enter` (option 1 is default).

**Dialog 2: Workspace trust** (first visit to a directory)
```
❯ 1. Yes, I trust this folder
  2. No, exit
```
**Action:** `tmux send-keys Enter` (default is correct).

**Dialog 3: Permissions bypass** (only with `--dangerously-skip-permissions`)
```
❯ 1. No, exit           ← default is WRONG
  2. Yes, I accept
```
**Action:** `tmux send-keys Down && sleep 0.3 && tmux send-keys Enter`.

**Dialog 4: Multi-select checkboxes** (context-gathering questions)
Appears mid-session. Number keys toggle options, Enter confirms, Tab moves sections.
**Prevention:** Be specific in your initial prompt so CC never needs to ask where to look.
- **`POLL_INTERVAL`** — seconds between polls (default: 10)
- **`SILENT_THRESHOLD`** — consecutive idle checks before assuming completion (default: 6 = ~60s)

### Key Differences from Manual Polling

| Aspect | Manual (section 2) | Automated Script |
|--------|-------------------|-----------------|
| Polling | 60-90s, Hermes does each poll | 10s, script does continuous polling |
| Questions | Hermes reads and decides | Script auto-answers with Enter (default) |
| Completion | Detected by idle timeout + manual check | Detected by output file existence |
| Cleanup | Manual | Script kills tmux, deletes temp files |
| Latency | 60-90s between polls | ~10s response to questions |

### When to Use

- **Cron jobs** — fully unattended runs
- **Long multi-phase tasks** — 10+ minutes total, many intermediate steps
- **Any scenario where CC may ask yes/no questions** — The script auto-advances through permission prompts and "okay to proceed?" type questions

### When NOT to Use

- Tasks requiring substantive decisions mid-run (the script only sends Enter; it can't choose between alternatives)
- Sessions where the user wants to observe CC's reasoning in real time
- Very short tasks (less than 2 minutes) where the overhead isn't worth it

## 7. Claude Code in Hermes Cron Jobs

A recurring pattern: the Hermes cron scheduler fires a job that spawns Claude Code to do periodic data-gathering + browser automation (team task planning, sheet updates, etc.). The cron job's Hermes agent orchestrates CC as a subprocess.

### Cron job structure

```yaml
cronjob(action='create',
  schedule:   "0 2 * * 0"          # cron expression in local timezone
  workdir:    "C:\\\\path\\\\to\\\\project"  # CC runs from here; file ops also start here
  deliver:    "origin"              # delivers results to the conversation thread
  prompt:     "..."                 # instructions for the cron's Hermes agent
)
```

**Pitfall — tick delay:** Hermes cron scheduler ticks every ~5-6 minutes. A job scheduled at `:01` may not fire until `:07`. This is normal and affects all jobs equally. The tick interval is visible in the gap between `next_run_at` and `last_run_at`.

**Pitfall — first-run bumped to next day:** Jobs created on the same day as their first scheduled slot may have `next_run_at` set to the following day instead. The scheduler sometimes skips the current day's window. Retry with `cronjob(action='run')` if immediate execution is needed, or schedule a few hours ahead of the intended first run.

### Session naming for multi-session concurrency

When running multiple CC sessions from the same cron template (e.g. 3x daily slots), use unique timestamped session names so prior sessions aren't killed:

```bash
TS=$(date +%Y%m%d-%H%M%S)
TMUX_SESSION="cc-${TS}"           # e.g. cc-20260711-083020
```

The startup phase should kill stale sessions matching the same prefix:

```python
# Kill only sessions older than N hours — let recent ones stay alive
for name in tmux_sessions():
    if prefix_match(name) and age_hours(name) > SESSION_MAX_AGE_H:
        kill_session(name)
```

**Why:** The end-user may be attached to prior sessions via Claude web remote control. Killing all `cc-*` sessions on spawn disconnects them mid-work. Only prune old ones.

The cron **prompt** (given to the Hermes agent) should be a straightforward script: write a prompt file, run CC, wait, read output, report. It does NOT need to reproduce the CC prompt inside itself — CC gets its own detailed prompt.

### Print mode with file-based prompts

For complex multi-phase Claude Code tasks (review + browser update), pass the prompt via a file rather than inline to avoid command-line quoting issues on Windows:

```bash
# Write the prompt file first (absolute Windows path to avoid MSYS /tmp confusion)
write_file(path="C:\\path\\to\\project\\cc_prompt.txt", content="...CC prompt...")

# Then invoke CC with $(cat file) expansion
cd /c/path/to/project && claude -p "$(cat /c/path/to/project/cc_prompt.txt)" \
  --model claude-sonnet-5 --chrome --max-turns 80 --max-budget-usd 8
```

**Pitfall — MSYS `/tmp` vs write_file:** On Windows git-bash, `write_file(path="/tmp/x.txt")` resolves to `C:\tmp\x.txt` (Windows-native path), while bash's `/tmp` maps to `%TEMP%` (e.g. `C:\Users\<user>\AppData\Local\Temp`). Always use the full project-relative or workdir path, not `/tmp/`, when the prompt file needs to be readable by bash. See `windows-hermes-setup` → MSYS `/tmp` mapping gotcha.

### `--chrome` flag — required for browser tools

Claude Code in print mode (`-p`) does NOT have browser/Chrome tools by default. Add `--chrome` to enable `mcp__claude-in-chrome__*` (navigate, computer, form_input, read_page, etc.):

```bash
claude -p "..." --chrome --model claude-sonnet-5
```

Without `--chrome`, the session reports "no browser/Chrome tool available" and cannot navigate to web pages or interact with browser-based apps (Google Sheets, Gmail, etc.).

**Known limitation:** `mcp__claude-in-chrome__*` works in print mode, but requires the user's Chrome browser to be running with the Claude-in-Chrome extension installed and authenticated (`claudeInChromeDefaultEnabled: true` and `hasCompletedClaudeInChromeOnboarding: true` in `~/.claude.json`).

### Turn & budget tuning for multi-phase tasks

Complex CC tasks that combine Gmail/Drive scanning + Chrome browser navigation + structured data entry need more headroom than simple coding tasks:

| Parameter | Simple task | Complex multi-phase | Reason |
|-----------|-------------|-------------------|--------|
| `--max-turns` | 10–20 | **60–80** | Browser interactions (navigate, read page, click cells) consume turns quickly |
| `--max-budget-usd` | 0.5–2 | **6–8** | Each browser MCP call adds token overhead; Sonnet 5 costs add up over 60+ turns |
| `--effort` | low | **medium** | Default; no need to override |

If the task hits `max-turns` before finishing, the output will say `"Error: Reached max turns (N)"` with partial work done. Increase and retry.

### Gmail/Drive connectors in print mode

Claude Code's cloud-side connectors (Gmail, Google Calendar, Google Drive — visible in `claude.json` as `claudeAiMcpEverConnected`) are available in print mode. No special flags needed — they work as long as the user's CC account has them connected via claude.ai.

**Detection:** If the connectors are available, CC will use them as tools. If they fail, CC reports something like "Gmail connector was invalidated and could not be searched." The fix is re-authenticating on claude.ai, not a CLI flag.

### Running CC from a cron job Hermes agent

The cron agent runs CC as a background PTY process:

```python
terminal(
    command="cd <workdir> && claude -p \"$(cat prompt.txt)\" --model ... --chrome --max-turns 80",
    background=True,
    pty=True,
    notify_on_complete=True,
    timeout=1200
)
```

Key considerations:
- **Timeout:** 1200s (20 min) minimum for complex tasks. CC needs this for cache creation + Gmail scanning + Drive scanning + browser work.
- **PTY required:** `pty=True` is needed for CC's terminal output, even in print mode.
- **notify_on_complete:** The cron agent's Hermes session needs this to know when to read the output and proceed.
- **Workdir:** Set the cron job's `workdir` to the project directory so file reads/writes and CC's initial cwd are in the right place.
- **Budget cap:** Always set `--max-budget-usd` to prevent runaway spend.

### Post-run: read CC-produced artifacts

After CC finishes, the cron agent should verify outputs (MD files, modified sheets, etc.) and report back. CC's stdout is available via `process(action='log')`, but the cron agent should also check for expected files on disk.

## 8. Provider / upstream error handling in cron jobs

### 8a. Transient provider errors

Cron-spawned Hermes agents can fail before the LLM even responds:

```
RuntimeError: HTTP 400: Error from provider (Console Go): Upstream request failed
```

**Cause:** The model API (e.g. deepseek-v4-flash over opencode-go) returned HTTP 400 — typically a transient gateway blip or payload validation on the model backend, not a Hermes bug.

**Characteristics:**
- Error appears in the cron output file at `~/.hermes/cron/output/<job_id>/<timestamp>.md` under `## Error`
- Agent never read its prompt or did any work — the LLM itself failed
- No tmux session created, no CC spawned, no artifacts
- Job `last_status` stays `ok` (the scheduler ran; the error is in the output)

**Response:**
1. Confirm the error includes the model/provider name
2. Retry: `cronjob(action='run', job_id='<id>')` — provider usually recovers within 5-15 min
3. If it fails again on retry, consider swapping the model or checking provider status

**What NOT to do:**
- Don't edit the prompt or re-create the job — the prompt was never sent
- Don't bump `agent.max_turns` — this isn't an iteration budget issue
- Don't restart the gateway — the gateway is fine, the provider isn't
- Don't confuse this with the "reached the maximum number of tool-calling iterations" warning — that's a different symptom (iteration budget, not provider error)

### 8b. Cron job output structure for failure diagnosis

Each tick writes to `~/.hermes/cron/output/<job_id>/<timestamp>.md`. The output file tells you exactly what went wrong:

| Indicator | Likely cause | Fix |
|-----------|-------------|-----|
| `## Error` with `HTTP 400` / `Upstream request failed` | Transient provider error | `cronjob(action='run')` |
| `## Response` truncated with "reached max iterations" | Hit `agent.max_turns` cap | `hermes config set agent.max_turns N` |
| `TASK_DONE: aborted` | Orchestrator aborted normally (no eligible tasks, browser unreachable) | No action |
| `TASK_DONE: partial` | Hit cap mid-close-out | Next cron slot continues via ledger |
| No output file at all | Gateway / cron scheduler crash | Check gateway.log |

**Tmux state persistence:** The orchestrator leaves tmux sessions alive when status is `done` or `partial`. Check with `tmux ls` and `tmux capture-pane -t <session> -p -S -40`.

**Ledger:** `<workdir>/cc-sessions/ledger.md` tracks task attempts. `tail -30` shows current state.

## 9. Orchestrator-prompt.md decoupling pattern

Best practice for complex CC cron jobs: keep the **deterministic shell instructions** in a separate `orchestrator-prompt.md` file, and have the cron job prompt just say "Read this file and execute it step by step."

**Structure:**
```
workdir/
├── cc-sessions/
│   ├── orchestrator-prompt.md     # deterministic steps
│   ├── ledger.md                  # task tracking
│   └── summary_<date>_<time>.md   # one per run
├── hermes-cc-pipeline-prompt.md   # CC session prompt (verbatim)
└── ...project folders...
```

**Advantages:**
- Cron prompt stays short — just reminders + the `read_file` instruction
- All procedural logic lives in one maintainable markdown file
- Multiple cron slots read the same orchestrator file
- CC's session prompt can be updated independently of orchestration logic

**Maintenance rule:** When updating `orchestrator-prompt.md`, also update the inline reminders in every cron job's `prompt` field. The cron agent reads the orchestrator file only once at startup, so in-cron reminders are the safety net.

## 10. Polling cadence for CC-in-tmux monitoring

Phase-specific intervals (at `agent.max_turns=150`):

| Phase | Interval | Rationale |
|-------|----------|-----------|
| Brainstorm/plan | 45s | CC processes questions in 10-30s |
| Execution | 60s | Plan phases complete in 2-5 min |
| Opencode handoff | 90s | Black-box subprocess |

**Optimizations:**
- Combine wait+read: `sleep N && tmux capture-pane -t cc-pipeline -p -S -40` (1 tool call)
- After answering a picker: give CC ~45s before re-polling
- `/usage` command: `tmux send-keys -t cc-pipeline "/usage" Enter` then `sleep 5 && tmux capture-pane`

**Budget math at 150:** ~15 setup + ~10 brainstorm + ~3 gate + ~15 monitoring + ~10 close-out = ~53 calls. Fits easily with ~97 calls to spare.

**If stuck at the default 60:** cap execution monitoring to ~8 polls (8 min), let CC run unattended for the rest. Verify side effects on the next cron slot.

## 11. Cron job retry pattern

```bash
cronjob(action='run', job_id='<job_id>')
```

Clean re-execution — respects existing config (provider, model, workdir, deliver target), spawns a fresh agent with full budget, reads the orchestrator prompt from scratch. Does NOT continue the previous run.

The retry's output gets a new timestamp entry in `~/.hermes/cron/output/<job_id>/`. If the job delivers to Discord/Telegram, the retry's output is delivered there.

## 12. Close out

### 12a. Verify side effects — never trust self-report

The agent's narrative summary (its "final report") may be wrong about what was actually accomplished. This includes:
- **Strikethrough:** the agent may claim it applied strikethrough when it didn't, or claim a cell is "fully struck" when only part of it is covered. Always verify via the API.
- **File writes:** the agent may claim it wrote a file when the write failed. Stat the file or read it back.
- **Sheet edits:** the agent may claim it updated a cell when the API call errored silently. Read the cell value.

**Real example (CC Pipeline, Jul 2026):** The orchestrator retry self-reported "2nd bullet — health checkup | Struck" in its status table. The actual cell state via `textFormatRuns` readback showed `strikethrough=False` from char 137 onward. The retry derived its status from a ledger scan, not from a fresh API check of the live formatting. Only an actual `includeGridData` readback caught the discrepancy.

**Rule:** A derived status ("the ledger says this was done") is NOT the same as a verified status. Always read back the actual resource state.

**Reference:** `references/sheets-includegriddata-bug.md` — the `gws` `includeGridData` range parsing bug and the two-tier read strategy (fast text scan → verified formatting readback).

### 12b. Multi-bullet cell edge case

The CC pipeline scanner reads cells by line-broken text (separated by `\n`). If a cell contains two bullets but the scanner resolves it as "1 bullet" with char range 0–136 covering only the first one, the second bullet (chars 137+) remains unstruck. The orchestrator's self-report may incorrectly claim the cell is "fully done."

**Mitigations:**
- When verifying strikethrough via `textFormatRuns`, check that EVERY character position has `strikethrough=true`, not just that the first run is struck.
- The final `\n` delimiter between bullets often falls outside the struck range. If the verification shows a clear `true` → `false` transition mid-cell, flag it.
- When the scanner lists "1st (only) bullet" for a cell, double-check the cell length. If the cell text is significantly longer than the claimed char range, there may be a second bullet the scanner missed.

### 12c. Standard close-out checklist

When the cron job fires:
- Verify artifacts exist (generated files, sheet changes, git state)
- Check CC stdout for errors or warnings
- Confirm ledger status was updated from `claimed` to final status
- Verify strikethrough via `textFormatRuns` readback — do not trust the agent's claim
- If strikethrough was partial or missing, re-apply via `gws sheets batchUpdate`
- Deliver a concise summary to the user showing what was done
- Mark any tracking todos as completed
