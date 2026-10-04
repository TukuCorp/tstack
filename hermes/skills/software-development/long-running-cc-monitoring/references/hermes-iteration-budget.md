# Hermes iteration budget — investigation notes

The companion to `long-running-cc-monitoring` section 5a. Captures the
specific knobs, file paths, and priority order for tuning the Hermes
agent's tool-call budget in cron-driven orchestration.

## What "iteration budget" means

A single Hermes agent run (one cron job tick, one user turn, one
subagent task) is allowed up to N tool calls before the runtime
synthesizes a forced final response. The user sees:

> You've reached the maximum number of tool-calling iterations allowed.
> Please provide a final response summarizing what you've found and
> accomplished so far, without calling any more tools.

The agent then writes a partial summary and exits. Any side effects the
agent was about to verify (summary files, ledger updates, sheet
strikethrough, etc.) are lost.

## Where the cap comes from

| Layer | Default | Source | Affects |
|-------|---------|--------|---------|
| Interactive TUI/CLI | 90 | `cli.py:12587` `getattr(agent, "max_iterations", 90)` | Direct TUI/CLI sessions |
| `HERMES_MAX_ITERATIONS` env var | 60 (injected by Hermes terminal snapshots) | `cache/terminal/hermes-snap-*.sh` | TUI/CLI sessions only |
| `config.yaml → agent.max_turns` | 60 (`config.yaml:9` in this install) | `cron/scheduler.py:2800` `max_iterations = _cfg.get("agent", {}).get("max_turns") or _cfg.get("max_turns") or 90` | **Cron-spawned agents** |
| CLI arg `--max-turns N` | wins over all config | `cli.py:3847` | Whatever session it was passed to |
| `config.yaml → delegation.max_iterations` | 50 (`config.yaml:419`) | `agent_init.py:492` | Subagents only |
| `goals.max_turns` | 20 | `config.yaml:428` | Goals-mode runs |

**The important asymmetry:** `HERMES_MAX_ITERATIONS` is read by the
interactive TUI/CLI agent path (`cli.py:3853`) but **not** by the cron
runner (`cron/scheduler.py:2800`). For cron jobs, the only knob is
`config.yaml → agent.max_turns` (or the CLI arg, which isn't relevant
for cron).

## The CC Pipeline pattern in particular

The CC Pipeline orchestrator uses ~5 calls for setup, then enters a
monitoring loop where each cycle is:

- `tmux send-keys ...` (1 call) — when a picker is detected
- `sleep N && tmux capture-pane ...` (1 call per poll)

A typical run:

| Phase | Polls | Setup | Total |
|-------|-------|-------|-------|
| Preflight + spawn CC | — | 3 | 3 |
| Brainstorm (6 picker questions, 4-6 polls) | 4-6 | 2 | 6-8 |
| Plan + usage gate | 2 | 2 | 4 |
| Execution monitoring (15 polls at 60s = 15min) | 15 | 2 | 17 |
| Strikethrough verification | — | 2 | 2 |
| Summary + close-out | — | 5 | 5 |
| **Total** | **~25** | **~16** | **~40-45** |

At the default `agent.max_turns=60`, this fits with ~15 calls of
headroom. At `max_turns=150`, you have ~105 calls of headroom and can
safely poll at 30-45s through execution.

## How to bump it for cron jobs

```bash
hermes config set agent.max_turns 150
hermes config show agent.max_turns
```

Edit the file directly is guarded:
> Refusing to write to Hermes config file. Agent cannot modify
> security-sensitive configuration. Edit `~/.hermes/config.yaml` directly
> or use `hermes config` instead.

So always use `hermes config set`. The change takes effect on the next
cron tick (the scheduler re-reads config at run time).

## The `no_agent=true` escape hatch

If monitoring CC is too heavy for the orchestrator budget no matter
how you tune it, convert the orchestrator's prompt into a Python
script and run it as a `no_agent=true` cron job. The script polls in a
plain Python loop with zero LLM involvement — no iteration budget is
consumed. See `references/auto-monitor-script-template.md` for the
pattern.

This is the right answer when:
- Polling is genuinely heavy (every 5-10s for 30+ minutes)
- The monitoring is fully deterministic (auto-answer picker → first
  option, no judgment needed)
- The verification is also deterministic (gws sheets API call, file
  existence check)

## The mistake to avoid

Don't waste time tweaking the cron job's `prompt` or the `.env` to try
to set `HERMES_MAX_ITERATIONS` for cron jobs. The cron runner doesn't
look at it. The right move is `hermes config set agent.max_turns N` or
move to `no_agent=true`.

## Sources

- `hermes-agent/cli.py:3846-3859` — `max_turns` priority chain
- `hermes-agent/cli.py:12587` — `getattr(self.agent, "max_iterations", 90)` fallback
- `hermes-agent/cron/scheduler.py:2800` — cron reads `agent.max_turns` only
- `hermes-agent/cron/scheduler.py:2955` — passed as `max_iterations=` to AIAgent
- `hermes-agent/agent/agent_init.py:177` — default `max_iterations: int = 90`
- `hermes-agent/agent/agent_init.py:291` — `agent.max_iterations = max_iterations`
- `config.yaml:9` — `agent.max_turns: 60` (this install)
- `config.yaml:419` — `delegation.max_iterations: 50` (subagent cap)
- `cache/terminal/hermes-snap-*.sh` — `HERMES_MAX_ITERATIONS=60` env injection
