---
name: verify-before-done
description: Prove work with a runnable check before calling it done, write briefs with a check, and bound unattended runs and review loops. Use when finishing any coding or automation task, writing a brief for a delegated or scheduled agent, or reviewing a diff.
version: 1.0.0
author: Tung Ho
---

# Verify before done

- End each task with a runnable check (test, build, script, screenshot) and show the command and its output as proof; "looks done" is not done.
- When a result falls short, escalate in order: add or tighten that check, then raise effort one level, then move up a model.
- Briefs (my prompts, subagent and swarm lanes, scheduled jobs) state Goal, Why, Constraints, Out of scope and Check. Leave out what the agent can read from the repo.
- Unattended runs (loops, swarms, scheduled jobs) also set a turn or spend limit and say where output lands for my approval. Pilot on about 3 items before running the rest.
- Review in a fresh context for correctness, not style. Cap review at 3 rounds, then review only the new diff. A finding that keeps recurring goes into a lint rule, the repo's `REVIEW.md`, or the skill that caused it.
- Delegate only substantial standalone work to subagents; do small jobs inline.
