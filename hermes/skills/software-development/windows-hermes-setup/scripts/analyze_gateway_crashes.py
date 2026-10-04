#!/usr/bin/env python3
"""Analyze gateway.log for session lifecycles and crash patterns.

Run: python analyze_gateway_crashes.py [days_back]
Default: 7 days.

Output: a table of session start times, uptimes, and last activity before
the next restart. The pattern of uptimes is the primary diagnostic signal
for distinguishing auto-start conflicts from real crashes.
"""
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path

LOG = Path.home() / 'AppData' / 'Local' / 'hermes' / 'logs' / 'gateway.log'
DAYS = int(sys.argv[1]) if len(sys.argv) > 1 else 7

if not LOG.exists():
    print(f"Log not found: {LOG}")
    sys.exit(1)

content = LOG.read_text(encoding='utf-8')
cutoff = datetime.now() - timedelta(days=DAYS)

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

print()
print(f"Total sessions in last {DAYS} days: {len([s for s in starts if datetime.strptime(s, '%Y-%m-%d %H:%M:%S,%f') > cutoff])}")
print()
print("Interpretation:")
print("  - Long uptimes (4-18h) with last activity = real crash (external termination)")
print("  - Short uptimes (<1h) clustered together = restart-loop conflict")
print("  - Long uptimes with NO ACTIVITY = idle survived; idle is NOT a cause")
