# Investigating Recurring Gateway Crashes — A Playbook

When the user reports "Discord bot is down" / "gateway crashed" repeatedly, the first move is to **investigate** before restarting. This playbook is the ordered sequence that worked on a real recurrence (37 sessions, multiple root causes) and is what to follow the next time the user says "investigate" or "what happened."

## Step 1 — Capture current state (do not restart)

```bash
# Gateway status
hermes gateway status 2>&1

# Is the gateway actually dead, or is it status lying?
ps aux | grep -E "hermes|gateway" | grep -v grep | head -5

# Are there lock files?
ls -la ~/AppData/Local/hermes/*.lock 2>/dev/null
```

Capture this BEFORE doing anything else. The user wants the actual state, not a fix.

## Step 2 — Look for evidence in the log

The gateway log at `%LOCALAPPDATA%\hermes\logs\gateway.log` is the primary source. The pattern to look for:

- **Cluster of `Starting Hermes Gateway...` events within 1-3 minutes** → restart loop conflict (the bash `.sh` + Scheduled Task + `Hermes.lnk` are all firing).
- **Single `Starting Hermes Gateway...` event after a long session** → real crash (external termination).
- **No events at all between long-running sessions** → gateway was idle, then the process disappeared with no warning.

**Distinguishing restart-loop conflicts from real crashes:**

| Signal | Restart-loop conflict | Real crash |
|---|---|---|
| Multiple `Starting Hermes Gateway...` events within 1-3 min | ✅ Common | ❌ Rare |
| "Another gateway instance is already running" errors | ✅ Diagnostic | ❌ Wouldn't see this |
| Uptime pattern in last 24h: bursts of 0.04h-0.5h sessions | ✅ Diagnostic | ❌ Single long session then gap |
| 4-18h uptime, last activity = inbound message or response ready | ❌ Doesn't match | ✅ Matches |

Use the script in `scripts/analyze_gateway_crashes.py` to extract this automatically.

## Step 2.5 — Check system memory (OOM diagnostic)

Silent gateway deaths with no error log can be caused by Windows terminating the process under memory pressure. Check before assuming a restart-loop conflict:

```bash
# Quick free-memory check
systeminfo | findstr "Available Physical Memory"

# Top memory consumers (watch out for bash $ expansion in PowerShell)
# Write to a file first to avoid MSYS variable expansion
echo 'Get-Process | Sort-Object WorkingSet -Descending | Select-Object -First 10 | Format-Table Name, WorkingSet -AutoSize' > $env:TEMP/memcheck.ps1
powershell -ExecutionPolicy Bypass -File $env:TEMP/memcheck.ps1
```

**Interpretation:**
- **<1.5 GB free on an 8GB system** = high risk of OOM kills. The gateway is one of the first processes terminated because Python processes are large (200-700MB).
- **Top 3 consumers are typically:** Chrome (multiple instances, 1.5GB+ total), Claude Code (3+ instances, 800MB+ total), Hermes Desktop (600-700MB).
- **Correlated evidence:** The log shows `✓ discord connected` → normal activity → process just stops with no error. No `Gateway exited` or traceback.

**OOM is likely when ALL of these are true:**
1. No error/exception logged — the process vanished
2. Available memory was <1.5GB when checked after the crash
3. At least one memory-heavy process (Chrome, Claude Code, Hermes Desktop) was active

**What NOT to do when OOM is suspected:**
- ❌ Don't blame the gateway code or restart loop
- ❌ Don't investigate auto-start conflicts (that's a separate pattern)
- ❌ Don't restart without also freeing memory — the new process will be killed too

**What to do instead:**
- Free memory by closing unused Chrome tabs and Claude Code sessions
- Check for orphaned Hermes.exe processes: `tasklist | findstr /i Hermes.exe`
- If OOM is chronic, recommend increasing pagefile or adding RAM

## Step 3 — Hypothesize before acting

Based on the log evidence, the most likely causes in order of frequency on Windows:

1. **3-way auto-start conflict** (most common). The `Hermes.lnk` in Startup folder launches the Desktop GUI which embeds a gateway. The `Hermes Gateway` Scheduled Task also fires. A bash `.sh` restart loop from a tmux session also fires. They fight for the lock; the bot comes up degraded or dies.
2. **Memory-pressure OOM kill** (second most common, often mistaken for #1). Windows terminates processes when available memory drops below ~1.5GB. The gateway vanishes with no log entry, no traceback, no exit code. Distinctive signal: the session-lifecycle table shows a single long session (4-18h) followed by a gap — not the cluster of short sessions that #1 produces. Check available memory with Step 2.5.
3. **Orphaned Hermes.exe processes** (exacerbates #2). Old `kill -9` from MSYS only kills the MSYS-side PID, not the Windows-native process. After hours, 5+ orphans consume 600MB+ each. Windows memory pressure kills the active one.
4. **External termination** (less common). Antivirus, Defender scan. Indistinguishable from #2 in the log.
5. **Idle itself is NOT a cause.** An 18h idle session that survived is direct evidence against this hypothesis. Don't waste time investigating it.

## Step 4 — Present findings to the user

Quote actual log lines and timestamps. Show the session-lifecycle table. State the hypothesis with evidence. **Do not act on auto-start sources without confirmation** — the triple-redundancy is a deliberate setup choice.

**Example framing:**

> "I see 3 `Starting Hermes Gateway...` events between 16:15 and 16:17 — that's a restart loop conflict, not a real crash. The most likely cause is the `Hermes.lnk` in Startup folder plus the `Hermes Gateway` Scheduled Task plus a bash `.sh` loop all firing. Before I touch any of those, can I show you what's there now?"

## Step 5 — Apply the fix (after user confirms)

Use the cleanup script: `scripts/remove_gateway_conflicts.cmd`. It runs as Administrator (UAC prompt) and:

1. Disables/deletes the `Hermes Gateway` Scheduled Task
2. Removes `Hermes.lnk` from Startup folder
3. Renames `Hermes_Gateway.cmd` to `.disabled` (no-op)
4. Creates a single new Scheduled Task: `Hermes Gateway Single` that runs `hermes gateway run` on logon
5. Verifies each step

The matching `scripts/hermes_gateway.sh` adds a PID-lock guard to the bash loop so it can't race the Scheduled Task.

## Step 6 — Verify

After the fix:

```bash
# Gateway up?
hermes gateway status 2>&1

# Discord connected?
grep 'discord connected' /c/Users/tukum/AppData/Local/hermes/logs/gateway.log | tail -1

# Only ONE gateway process
ps aux | grep -E "hermes.*gateway" | grep -v grep | wc -l   # should be 1
```

## What NOT to do

- ❌ Don't restart the gateway before investigating. The user wants logs read first.
- ❌ Don't disable auto-start sources without confirmation. The triple-redundancy was a deliberate decision and the user is protective of it.
- ❌ Don't claim "fixed" without showing the verification output.
- ❌ Don't change the user's default provider as a "test." If a provider is failing, fix its config (`.env` `BASE_URL` vs `API_KEY` mixup, `config.yaml` provider/base_url mismatch) — don't swap to a different one.
- ❌ Don't say "the gateway crashes when idle" without first showing the session-lifecycle table. Idle is a common user hypothesis that the data usually disproves.

## Reference: the user's diagnostic preferences

Captured from repeated sessions:

- Wants investigation **first**, restart **second**.
- Expects to see actual log lines, not summaries.
- Pushes back on tone-deaf conclusions (e.g. "fixed" before verification).
- Appreciates evidence-based ruling-out of causes ("the 18h idle session proves idle isn't the cause").
- Will accept a clean diagnostic table over a long prose explanation.
