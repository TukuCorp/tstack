# System/Configuration Investigation for Hermes

When the user reports a Hermes issue (connection errors, model switches, cron failures), use this investigation flow.

## Phase 1: Gather Evidence (before any fix)

### 1. Read the gateway log

```bash
tail -50 ~/AppData/Local/hermes/logs/gateway.log
```

Don't just tail — search with time windows and event types:

```bash
# Find all model-related events today
grep -E 'model|switch|provider|slash' ~/AppData/Local/hermes/logs/gateway.log | grep '2026-07-06'

# Find all errors today
grep -E 'error|failed|Connection error|API call' ~/AppData/Local/hermes/logs/gateway.log | grep '2026-07-06'

# Find all /model invocations in Discord
grep "slash '/model'" ~/AppData/Local/hermes/logs/gateway.log

# Find all cron job activity
grep 'cron.scheduler' ~/AppData/Local/hermes/logs/gateway.log | tail -10
```

### 2. Check current state

```bash
# What does config say?
grep -A 5 '^model:' config.yaml

# What does .env say?
grep 'OPENCODE_GO\|API_KEY\|SECRET\|TOKEN' .env | grep -v '^#'

# Is gateway running?
hermes gateway status

# Any other hermes processes?
ps aux | grep hermes | grep -v grep
```

### 3. Reconstruct the timeline

- Start from the first abnormal log entry, not the latest
- Trace forward: what happened *after* the first error?
- Look for convergence: what do multiple errors point to? (same provider, same endpoint, same config key)

## Phase 2: Identify Root Cause

Common patterns to check:

| Pattern | How to detect |
|---------|---------------|
| **Env var key-in-URL** | `grep 'BASE_URL' .env` — if value starts with `sk-` or similar, it's a key not a URL |
| **Provider/URL mismatch** | `grep -A 5 '^model:' config.yaml` — confirm base_url matches the provider's real endpoint |
| **Double gateway** | Log shows repeated `"Another gateway instance is already running (PID XXXX)"` |
| **Cron drift guard** | Log shows `"Skipped to prevent unintended spend"` — job was created with different model |
| **Discord delivery 404** | Log shows `"Discord API error (404): Unknown Channel"` — delivery to invalid DM/channel |
| **Bot DM not working for cron** | Cron with `deliver='all'` or `deliver='discord:USER_ID'` fails — cron can't fabricate a DM context |

## Phase 3: Fix

1. Fix one thing at a time
2. Verify after each fix — check logs for new errors
3. Restart gateway after config changes

```bash
# Set all three model config values consistently
hermes config set model.default <model>
hermes config set model.provider <provider>
hermes config set model.base_url <correct-endpoint>

# Verify
grep -A 5 '^model:' config.yaml

# Restart gateway
ps aux | grep hermes | grep -v grep | awk '{print $1}' | xargs -r kill -9
```
