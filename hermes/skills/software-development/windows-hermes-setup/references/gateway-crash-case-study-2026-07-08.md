# Gateway Crash Case Study — 2026-07-08

A real-world investigation of recurring gateway disconnects on a Windows machine running Hermes. The user's Discord bot appeared to "crash" repeatedly over 24 hours. This documents the full investigation sequence, the false leads ruled out, the actual root cause, and the fix that stuck.

The methodology here is the one to reuse for any "gateway is down" report — follow the same sequence, capture the same evidence, present the same kind of table.

## Initial state

User reported: "discord bot seem down, investigate"

What was actually wrong on first check:
- `hermes gateway status` → `✗ Gateway is not running`
- Log showed `✓ discord connected` at the last entry, but no follow-up
- No FATAL, ERROR, or traceback in the log
- No Windows Event Log entry

The gateway had just disappeared. No error trail. This is the symptom that triggers the playbook.

## Investigation sequence

### Step 1 — Pulled the timeline

```bash
grep -E 'Starting Hermes Gateway|✓ discord connected' gateway.log
```

Extracted pattern from the last 24h of log:

| Time | Uptime since previous start |
|------|------------------------------|
| Jul 8 04:34 → 10:41 | 6.07h |
| Jul 8 10:41 → 12:02 | 1.37h, no activity |
| Jul 8 12:02 → 16:15 | 4.20h, last activity 15:28 |
| Jul 8 16:15 → 16:17 | 0.04h, no activity |
| Jul 8 16:17 → 16:47 | 0.51h, no activity |

Two distinct failure modes appeared:
- **0.04h and 0.51h sessions with no activity** = restart-loop conflict
- **4.20h session with last activity at 15:28** = real crash, not idle

### Step 2 — Ruled out the false leads

The "idle causes crashes" hypothesis was tempting because the 16:17→16:47 session had no traffic. But the same log showed an 18h session with zero activity on Jul 7 that survived. So idle is not a cause.

Power config was checked too:
```bash
powercfg /QUERY SCHEME_CURRENT SUB_SLEEP
# Current AC Power Setting Index: 0x00000000   # never sleep
# Current DC Power Setting Index: 0x00000000   # never sleep
```

User confirmed laptop did not hibernate. So sleep/hibernate is not a cause.

### Step 3 — Found the smoking gun

In every short session, the log showed:
```
2026-07-08 16:15:16  gateway.run: Recovered 1 background process(es) from previous run
2026-07-08 16:15:21  ✓ discord connected
2026-07-08 16:17:37  gateway.run: Starting Hermes Gateway...   ← new gateway, 2 min later
2026-07-08 16:17:42  ✓ discord connected                          ← second one connects
2026-07-08 16:47:57  gateway.run: Starting Hermes Gateway...   ← third one
2026-07-08 16:48:02  ✓ discord connected                          ← it disconnects the second
```

Multiple `Starting Hermes Gateway...` events within minutes of each other, each followed by `✓ discord connected`, with no `Gateway exited` in between. The gateway isn't crashing — it's being **disconnected by a competing gateway instance connecting on the same lock**.

The "Recovered 1 background process(es) from previous run" line was the tell. The gateway is recovering a child process and treating it as fresh. When two sources race, the second one kicks the first off Discord. The first then dies silently when it loses the connection.

### Step 4 — Counted the sources

Three independent sources were spawning gateways:

```bash
ls "/c/Users/tukum/AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Startup/"
# Chrome_Beta.cmd
# desktop.ini
# Hermes.lnk                                              ← source 1

schtasks /query /tn "\Hermes Gateway" 2>&1 | grep TaskName
# TaskName: \Hermes Gateway                                ← source 2
# Action: Hermes_Gateway.cmd (which has its own restart loop)

ls /c/Users/tukum/AppData/Local/hermes/gateway-service/
# Hermes_Gateway.cmd                                       ← source 3
# hermes_gateway.sh                                        ← source 4
```

Four sources, all spawning gateways, all fighting for the same lock. The `hermes_gateway.sh` bash loop I had previously added as a "resilience layer" was actually the most active competitor — it had no PID-lock guard, so it tried to start every 5-10 seconds regardless of whether one was already running.

## The fix

Per the SKILL.md "Gateway Restart Loop Conflicts" section, the resolution is **single-ownership**: pick ONE source and disable the rest.

The chosen single source: a new Scheduled Task that runs `hermes gateway run` directly on logon, plus a PID-lock-guarded bash loop for crash recovery.

### Cleanup commands

```powershell
# Requires UAC elevation — wrap in Start-Process -Verb RunAs

# 1. Delete the conflicting Scheduled Task
schtasks /Delete /TN "\Hermes Gateway" /F

# 2. Remove Hermes.lnk from Startup folder
Remove-Item "C:\Users\tukum\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\Hermes.lnk"

# 3. Disable the .cmd restart script
Rename-Item "C:\Users\tukum\AppData\Local\hermes\gateway-service\Hermes_Gateway.cmd" `
            "C:\Users\tukum\AppData\Local\hermes\gateway-service\Hermes_Gateway.cmd.disabled"

# 4. Create the single clean Scheduled Task
schtasks /Create /TN "Hermes Gateway Single" `
         /TR "C:\Users\tukum\AppData\Local\hermes\hermes-agent\venv\Scripts\hermes.exe gateway run" `
         /SC ONLOGON /RL HIGHEST /F
```

The bash restart script (`hermes_gateway.sh`) was kept as the recovery layer but with the PID-lock guard added so it won't race the Scheduled Task:

```bash
while true; do
    if [ -f "$LOCK_FILE" ]; then
        EXISTING_PID=$(python -c "import json; print(json.load(open(r'$LOCK_FILE'))['pid'])" 2>/dev/null)
        if [ -n "$EXISTING_PID" ] && ps -p $EXISTING_PID > /dev/null 2>&1; then
            echo "[$(date)] Gateway already running (PID $EXISTING_PID), skipping"
            sleep 30
            continue
        fi
    fi
    echo "[$(date)] Starting Hermes Gateway..."
    /c/Users/tukum/AppData/Local/hermes/hermes-agent/venv/Scripts/hermes.exe gateway run
    sleep 10
done
```

The guard reads the JSON lock file written by `hermes.exe` at startup and refuses to spawn a duplicate while that PID is alive. The bash loop then becomes a no-op as long as the gateway is up, only actually starting one if the process dies.

## Verification

After the fix:
```bash
hermes gateway status
# ✓ Gateway is running (PID: 32084)

grep 'discord connected' gateway.log | tail -1
# 2026-07-08 17:04:41  ✓ discord connected

ps aux | grep "hermes.*gateway" | grep -v grep | wc -l
# 1                       ← only one gateway
```

The bash loop's `[$(date)] Gateway already running` log lines were the visible signal that the guard was working — every 30 seconds it would log the same "skipping start" message while the live gateway stayed healthy.

## What the user pushed back on

This case had a real user correction worth recording:

1. **"i was not using nous before"** — when I tried to "fix" the failing provider by switching the default to `stepfun` via `nous`, the user called out that they were on `opencode-go` and I had no business changing the default. The right move was to fix `OPENCODE_GO_BASE_URL` (which was set to the API key value), not swap providers.

2. **"i'll test discord with command model now"** — the user then tested `/model` in Discord themselves. They knew exactly what to do. Don't second-guess the user's tooling; the investigation phase is to find the bug, not redesign the setup.

3. **"is discord bot connected?" repeated** — after each restart, the user wanted the actual `hermes gateway status` output and the `grep` line, not a one-word "yes." Show the evidence.

## What this case study reinforces for future sessions

- **Investigation first, restart second.** Always. The user will pull the log themselves if you don't show it.
- **Don't change defaults you weren't asked to change.** A provider/endpoint config fix is not the same as a provider swap.
- **The 3-way auto-start conflict is the most common cause on Windows.** When the user reports "crashes" but the log shows no error, check for competing sources before hunting for code bugs.
- **Idle is not a cause.** 18h idle sessions that survive are direct evidence. State this to the user when it's relevant.
- **The bash restart loop is the resilience layer, not a duplicate of auto-start.** Without the PID-lock guard, it competes. With the guard, it only fires on real exits.
