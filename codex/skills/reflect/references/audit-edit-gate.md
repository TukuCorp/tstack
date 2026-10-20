# Edit gate for audit mode

Adapted from skill-doctor's `skill-improvements.md` (MIT, warpdotdev/common-skills), with the structural-mechanism check from session mode's synthesizer.

## Method

1. Cluster the failed-conversation findings by root cause, across scorers.
2. Prioritize clusters by frequency times severity.
3. Verify each finding against the current repository and the agent's configuration before proposing anything. Drop what does not verify.
4. You are editing another agent's instructions. Keep edits small and general. State the intended behavioral rule and the owning surface in one sentence, then make the smallest change that expresses it.
5. Prefer replacing existing guidance over appending another paragraph.

## When to propose a change

Do not propose changes by default. Proceed only when a concrete instruction is missing or wrong and amending it would have prevented the scored failure. Ask: would a competent agent with the current instructions still be expected to fail this way? If yes, there is a gap. If no, defer.

File only when all of these hold:

- The failure comes from a missing, wrong or underspecified instruction on a concrete surface: the agent's configuration, a skill, or in-repo guidance.
- You can name that surface and the one reusable rule it should have stated.
- Had that rule been present and followed, the scored failure would not have happened.
- The same gap appears in more than one session, or is severe enough that a single occurrence proves a missing contract.

Do not file when:

- The existing instruction already required the correct behavior and the model ignored it.
- The failure is model variance: same prompt, same tools, different choice.
- The only available edit is restating, hedging, or adding examples from these runs.
- The real fix is product, infra, scorer or code outside instruction surfaces.
- A lint rule, script, hook, metadata flag or runtime check would enforce the rule more reliably than prose. Route it to Backlog instead.

An installed skill that never triggered in a failed conversation is usually a description problem: propose a `tune description` edit that front-loads the trigger phrases the user actually used.

When nothing clears the bar, open no change and say, per finding, why not. That is a success. A speculative change is worse than none.
