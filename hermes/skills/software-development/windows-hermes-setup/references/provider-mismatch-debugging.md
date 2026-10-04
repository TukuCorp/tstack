# Provider / Base URL Mismatch — Case Study

## The Symptom

After running `/model deepseek-v4-flash` in Discord, all API calls failed with `Connection error`. Gateway restarts didn't help. The model appeared to switch erratically between `opencode-go` and `nous`.

## Timeline (abridged)

| Time | Event |
|------|-------|
| 04:07 | User invoked `/model` (normal workflow) |
| 04:10 | User invoked `/model` again |
| 05:41 | User invoked `/model` — asking about provider issues |
| 05:56 | Gateway restart |

## Root Cause: Two Independent Bugs

### Bug 1: Env var key-in-URL

`OPENCODE_GO_BASE_URL` in `.env` was set to the API key (`sk-oFl...Jxm0`) instead of the endpoint URL (`https://opencode.ai/zen/go/v1`). Every API request from opencode-go went to a URL that was garbage → immediate connection failures.

**Detection:**
```bash
grep 'OPENCODE_GO_BASE_URL' .env
# → OPENCODE_GO_BASE_URL=sk-oFl...Jxm0   ← WRONG
```

**Fix:** Set to the real endpoint:
```env
OPENCODE_GO_BASE_URL=https://opencode.ai/zen/go/v1
```

### Bug 2: Provider/base_url mismatch in config.yaml

When `/model` was used, it saved the selected provider AND base_url to `config.yaml`. But the base_url for `opencode-go` was wrong (Bug 1). Later, when `nous` was selected as provider, the old (wrong) base_url stuck around:

```yaml
provider: nous
base_url: https://opencode.ai/zen/go/v1   # ← Mismatch
```

The `nous` provider sent requests to the OpenCode endpoint, which rejected them.

**Detection:**
```bash
grep -A 5 '^model:' config.yaml
```

**Fix:** Set all three together so they stay consistent:
```bash
hermes config set model.default stepfun/step-3.7-flash:free
hermes config set model.provider nous
hermes config set model.base_url https://inference-api.nousresearch.com/v1
```

## Cascade Effects

1. **Cron drift guard blocked heartbeat** — The cron job was created when model was `deepseek-v4-flash`. When global model changed to `nous/stepfun`, the drift guard skipped execution.
2. **Discord 404 on delivery** — The heartbeat tried to deliver to a DM channel that doesn't accept standalone cron messages — `Discord API error (404): Unknown Channel`.
3. **Gateway silent exit** — After handling 200+second tasks with ~270K token contexts, the gateway exited cleanly at ~12:03 with no crash trace. The restart loop recovered it but startup then hung due to a stale `auth.lock` file. Removing the lock file resolved the hang.

**Fixes:**
- Pin cron jobs at creation: `cronjob action=update job_id=xxx provider=nous model=stepfun/step-3.7-flash:free`
- Set cron delivery to `local` if no valid Discord channel exists for delivery
- Remove stale `auth.lock` on gateway hang: `rm -f ~/.hermes/auth.lock`

## Prevention

1. **Verify after every `hermes config set`** — run `grep -A 5 '^model:' config.yaml` to confirm provider + base_url match
2. **Don't use `/model` across dissimilar providers** — it rewrites `base_url` globally and can leave orphan mismatches
3. **Pin cron jobs to models explicitly** — prevents drift guard from blocking them silently
4. **Check `.env` for key-in-URL** — when adding a new provider, verify the `BASE_URL` variable contains a URL, not the API key
