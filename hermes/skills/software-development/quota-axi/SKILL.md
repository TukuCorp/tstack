---
name: quota-axi
description: "Check how much subscription quota is left on Claude, Codex, Antigravity (agy) and other local agent providers, when each window resets, and whether the current pace runs out before then, via the quota-axi CLI. Use before a long, parallel or unattended run (swarms, loops, scheduled jobs), before choosing which provider or model gets a big job, and when the user asks about usage, rate limits or remaining quota. Data only; the decision stays yours."
version: 1.0.0
author: tukum (TukuCorp)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [quota, rate-limits, observability, cli]
    related_skills: [necro]
---

# quota-axi

`quota-axi` reads the local agent CLIs' own credentials and asks each provider's first-party usage endpoint what is left. It never routes, logs in or mints credentials. It is installed globally (`npm i -g quota-axi`); if `quota-axi` is not found, use `npx -y quota-axi` with the same flags.

## Commands

- `quota-axi` - every provider that is set up on this machine.
- `quota-axi --provider claude` (or `codex`, `agy`, comma-separated) - one or a few lanes; faster.
- `quota-axi models` - per-model rows joined with quota (which models share a pool).
- `quota-axi --json` / `--full` - normalized model, per-window pace and evidence.
- `quota-axi auth` - which credential sources were found, without printing secrets.
- Add `--max-age 5m` when you check repeatedly in one run, so a recent reading is reused instead of asking the vendor again.

## Reading the default output

- `quota[]`: one row per scope. `effectivePercentRemaining` is the minimum across the windows that bind it (session, weekly, monthly); `limitedBy` names the window that is tightest; `resetsAt` is when it resets.
- `runway`: `through_reset` means the current pace lasts until the reset; `projected_exhaustion` means it runs out first. The `exhaustion[]` block then gives `usableRunwaySeconds` and `projectedExhaustedAt`.
- `spendPriority`: above 0 means headroom will likely go unused before the reset (good place to spend); below 0 means the lane is on track to run out. Rows are not sorted; compare them yourself.
- `confidence: early` means little usage history yet; treat runway as a rough guess.
- `attention[]`: lanes that need sign-in, are stale, or cannot be measured.

## How to use it

- Before a run that will burn quota fast (several agents, a loop, an overnight job), check the lanes you plan to use. If a lane shows `projected_exhaustion` within the run's expected length, tell the user and suggest another lane or a smaller run before launching.
- Mid-run, re-check with `--max-age 5m` rather than on every step.
- Report what you read in plain terms: percent left, the binding window, reset time, and runway.
- Do not pass `--allow-keychain-prompt` without asking the user; it reads OS credential stores.

Adapted from kunchenguid/quota-axi (MIT).
