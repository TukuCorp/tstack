---
name: verify
description: Independently verify that a completed task's claims are actually true, from a fresh evidence-gathering pass — never trusting prior conversation as evidence. Reproduces evidence by running the repo's own tests, inspecting git diff/log, and checking claimed artifacts, then emits a verified/partial/refuted verdict with a reports/verify-*.md file. Use when the user explicitly invokes `/verify`, or asks to double-check, confirm, or independently validate that a change actually works after any agent-driven change when you need to trust "done" rather than assume it.
---

# Verify

## Purpose

Produce an independent, evidence-based verdict on whether a completed piece of work
actually did what it claims to have done. This skill exists because agents
(including this one, in prior turns) can report success without having actually
achieved it — a wrong diff, a test that was never run, an artifact that was never
written. `/verify` treats every prior claim as unproven until it is freshly
reproduced in this run.

**The one rule that matters: conversation history is not evidence.** Only commands
executed during THIS invocation of `/verify`, against the current state of the
repo on disk, may support a verdict. If you "remember" that tests passed, that
memory does not count — run them again, right now.

## Trigger

- Run only on explicit `/verify`.
- Treat the user's arguments as the claims/task description to verify.

## Procedure

### 1. Identify the claims to check

Determine what is being verified, in this priority order:

1. If arguments were given, use them directly as the task description and/or
   the specific claims to check.
2. Otherwise, look for the most recent `## Review` or `## Results` section in
   `activeContext.md` at the repo root, if that file exists.
3. Otherwise, run `git log --oneline -3` and treat the most recent commit
   message(s) as the claim(s) to verify (e.g. "fixed the retry bug" implies
   "the retry bug is fixed and covered by a passing test").

If none of these yield anything concrete, ask the user what to verify and stop —
do not invent claims to check.

Break the claims down into a short list of discrete, checkable statements. Example:
a claim like "added the feature and all tests pass" becomes two statements:
(a) the feature exists in the diff, (b) the full test suite passes.

### 2. Reproduce evidence for each claim

For every claim, take actions that could actually falsify it — do not just read
code and eyeball plausibility. Use whichever of these apply:

- **Tests claimed to pass:** find and run the repo's actual test command (check
  `README`, `package.json` scripts, `pyproject.toml`, `Makefile`, or CI config for
  the exact command — do not guess `pytest` vs `uv run pytest` vs `npm test`).
  Capture the real exit code and the tail of output.
- **Code/feature claimed to exist:** run `git diff <base>..HEAD --stat` and
  `git diff <base>..HEAD` (or `git status --porcelain` + `git diff` for uncommitted
  work) and confirm the claimed change is actually present in the diff, not just
  described in a commit message.
- **Artifact claimed to be created/updated:** check the file exists on disk, has
  non-zero size, and — if the claim specifies content — actually contains it
  (`grep` for the expected string, or parse it if structured).
- **Bug claimed fixed:** if a regression test is claimed, run just that test in
  isolation and confirm it passes; if no test exists for it, that itself is
  evidence the claim is unverifiable, not verified.
- **No test files were altered to force a pass:** check whether the diff touches
  `tests/**`, `test_*`, `*_test.*`, `conftest.py`, or spec files in ways that look
  like the test was weakened rather than the code fixed. If so, flag it explicitly
  as suspicious evidence, not supporting evidence.

A claim with no way to obtain evidence for it (unclear test command, ambiguous
scope, no diff to inspect) counts as **not reproduced** — fail closed. Do not give
the benefit of the doubt.

### 3. Determine the verdict

- **verified** — every claim has reproduced, non-contradicting evidence.
- **partial** — at least one claim has reproduced evidence, and at least one does
  not (or could not be reproduced).
- **refuted** — no claim could be reproduced, OR any claim is directly contradicted
  by what you observed (e.g. "tests pass" but the suite actually fails; "feature X
  added" but the diff shows no such change; a test was edited to force a pass).

### 4. Write the verdict file and report

Write `reports/verify-YYYYMMDD-HHMM.md` (create the `reports/` directory if it
doesn't exist) with:

```markdown
---
verdict: verified|partial|refuted
date: "{{ISO-8601 timestamp with local offset}}"
claims_checked: {{n}}
---

# Verify: {{one-line summary of what was checked}}

## Claims
1. {{claim}} — {{reproduced|not reproduced|contradicted}}
2. ...

## Evidence
- `{{exact command run}}` -> {{observed result, quoting real output where useful}}
- ...

## Verdict
{{verified|partial|refuted}} — {{one or two sentences explaining why}}
```

Then print to the user, exactly:

```
VERDICT: {{verified|partial|refuted}}
CLAIMS_CHECKED: {{n}}
EVIDENCE:
- {{command}} -> {{result}}
- {{command}} -> {{result}}
```

## Anti-Patterns

- Do not run `/verify` from the same context/session that did the work and rely
  on your own memory of having already run the tests — this skill's entire value
  is in re-executing checks, not recalling them.
- Do not soften a `refuted` verdict to `partial` because the work was "close."
  Report what the evidence shows.
- Do not skip claims because checking them is inconvenient. An unchecked claim is
  a claim without evidence, which drives the verdict toward `partial`/`refuted`,
  not toward silently passing.
