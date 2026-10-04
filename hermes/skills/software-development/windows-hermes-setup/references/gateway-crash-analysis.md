# Gateway Crash Analysis — Reading Session Lifecycles

When the user reports "Discord bot is down" or "gateway keeps crashing" with **no error logs**, the standard log-grep approach (`grep -i error gateway.log`) returns nothing useful. Use this technique to reconstruct what happened from the only signals you do have: the start/connect/restart cycle.

## The Core Technique: Session Lifecycle Extraction

The gateway's last log entry is always a normal operation (e.g. `response ready`). The first signal of a crash is the **next** `Starting Hermes Gateway...` event. Between these, the process silently exited.

```python
# Pseudocode — adapt path to your log location
import re
from datetime import datetime

log = open(r'C:\Users\tukum\AppData\Local\hermes\logs\gateway.log', encoding='utf-8').read()

# 1. Find all startup events
starts = re.findall(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) INFO gateway.run: Starting Hermes Gateway', log)

# 2. Find all inbound/response events
events = re.findall(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) INFO (gateway.run:[a-z\._]*|hermes_plugins\.discord_platform\.adapter: \[Discord\] Flushing text batch).*', log)

# 3. For each session, compute uptime = next_start - this_start
# 4. For each session, find the last non-housekeeping event before the next restart
```

**Output a table:**

```
Session | Start time           | Next start          | Uptime    | Last activity
# 1     | 2026-07-07 05:20:55 | 2026-07-07 23:30:42 |  18.16h   | NO ACTIVITY IN SESSION
# 2     | 2026-07-08 12:02:59 | 2026-07-08 16:15:16 |   4.20h   | 15:28:53: response ready
# 3     | 2026-07-08 16:15:16 | 2026-07-08 16:17:37 |   0.04h   | NO ACTIVITY IN SESSION  ← crash chain
```

## Reading the Output

Three patterns emerge from a real investigation (37 sessions over 2 weeks):

| Pattern | Uptime | Last activity | Meaning |
|---------|--------|---------------|---------|
| **Long sessions, no activity** | 4-53h | May be empty | Gateway stayed connected idle for hours — idle itself is **not** a cause |
| **Short sessions, no activity** | 0.01-0.5h | Empty | Crash chain from active troubleshooting (`.cmd` vs `.sh` restart loops fighting) |
| **Long sessions, with activity** | 4-18h | Last response ready | Normal crash after processing a message — likely process-level kill |

## What to Check When All Sessions Are "Long + No Activity"

The "idle kills gateway" hypothesis is **not supported by evidence** if you find 18h+ idle sessions that survived. Real causes to investigate:

| Cause | How to confirm |
|-------|----------------|
| **Another gateway instance conflict** | `grep 'Another gateway instance' gateway.log` — repeated same PID in error messages |
| **Orphaned Hermes.exe processes** | `tasklist /FI "IMAGENAME eq Hermes.exe"` — if count > 4 with high memory, accumulation is killing the active one |
| **Stale lock files blocking startup** | After crash, `ls -la ~/.hermes/*.lock` — `auth.lock` or `gateway.lock` may persist, blocking new starts |
| **Windows power/network adapter sleep** | `powercfg /QUERY SCHEME_CURRENT SUB_SLEEP` — check "Sleep after" value; also check `netsh interface show interface` for power management |

## What Does NOT Cause Silent Crashes

Don't waste time investigating these — they're ruled out by evidence:

- ❌ **Cron job failures** — only affect that job, not the gateway process
- ❌ **Single message volume** — 200+ second responses don't cause gateway death
- ❌ **Token usage** — 270K+ token contexts are normal
- ❌ **Antivirus scans** — would show in Windows Event Log
- ❌ **Sleep/hibernate** (when user has confirmed it didn't happen)

## The Smoking Gun: Outdated Investigation Scripts

A common red herring: the user shares error logs from a CC Pipeline cron job session (`gen_send_cmd.py` errors, `Tool terminal returned error`). These are **task-level** errors, not **gateway-level** failures. The gateway has been running fine through them.

**How to tell them apart:**
- **Gateway crash**: process disappears, `hermes gateway status` returns "not running"
- **Task error**: gateway is still running, but the conversation/task log has errors

## The Cleanest Fix Pattern

Once you've extracted the session lifecycle, the recovery is one command:

```bash
# Clean up after a crash
ps aux | grep hermes | grep -v grep | awk '{print $1}' | xargs -r kill -9
rm -f ~/AppData/Local/hermes/auth.lock
rm -f ~/AppData/Local/hermes/gateway.lock
rm -f ~/AppData/Local/hermes/kanban/.dispatcher.lock

# Verify only the Desktop GUI's Hermes.exe remains
tasklist /FI "IMAGENAME eq Hermes.exe" 2>&1 | tail -n +4

# Start fresh
hermes gateway run
```

If crashes repeat, the user needs to be told the gateway is dying from something external (antivirus, defender scanning, Windows resource pressure) — the only durable fix is to add diagnostic instrumentation that captures the actual termination signal.

## A Pre-Made Script

Save this as `~/.hermes/scripts/analyze_gateway_crashes.py` for one-shot analysis:

```python
#!/usr/bin/env python3
"""Analyze gateway.log for session lifecycles and crash patterns."""
import re
import sys
from datetime import datetime
from pathlib import Path

LOG = Path.home() / 'AppData' / 'Local' / 'hermes' / 'logs' / 'gateway.log'
DAYS = int(sys.argv[1]) if len(sys.argv) > 1 else 7

content = LOG.read_text(encoding='utf-8')
cutoff = datetime.now() - __import__('datetime').timedelta(days=DAYS)

starts = re.findall(
    r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) INFO gateway.run: Starting Hermes Gateway',
    content,
)

activity_pat = re.compile(
    r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) INFO '
    r'(gateway.run:[a-z\._]*|hermes_plugins\.discord_platform\.adapter: \[Discord\] Flushing).*'
)
events = activity_pat.findall(content)

print(f"{'#':<3} {'Start':<20} {'Next start':<20} {'Uptime':<8} {'Last activity'}")
print("-" * 130)

for i, start in enumerate(starts):
    if i + 1 >= len(starts):
        break
    start_ts = datetime.strptime(start, '%Y-%m-%d %H:%M:%S,%f')
    if start_ts < cutoff:
        continue
    next_ts = datetime.strptime(starts[i+1], '%Y-%m-%d %H:%M:%S,%f')
    uptime = (next_ts - start_ts).total_seconds() / 3600

    last = None
    for ts_str, msg in events:
        ts = datetime.strptime(ts_str, '%Y-%m-%d %H:%M:%S,%f')
        if start_ts <= ts < next_ts and 'housekeeping' not in msg.lower() and 'kanban' not in msg.lower():
            last = (ts_str, msg[:50])

    la_str = f"{last[0][:19]}: {last[1]}" if last else "NO ACTIVITY"
    print(f"#{i+1:<2} {start[:19]:<20} {starts[i+1][:19]:<20} {uptime:>6.2f}h {la_str}")
```

Run:
```bash
python analyze_gateway_crashes.py 7   # last 7 days
python analyze_gateway_crashes.py 14  # last 14 days
```

## Talking to the User About Findings

When you present results, frame conclusions in terms of **what the evidence rules out**, not what it confirms:

- "The 18h idle session proves idle alone doesn't kill the gateway"
- "The 4-6h uptime pattern matches external termination (defender scan, memory pressure) but I cannot prove which without ETW trace"
- "All short sessions cluster around your troubleshooting windows — those crashes were caused by me, not the system"

The user has likely already debugged the obvious causes. Your job is to help them rule things out, not invent a new theory.
