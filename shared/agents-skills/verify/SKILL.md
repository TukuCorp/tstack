---
name: verify
description: Independently verify that a completed task's claims are actually true, from a fresh evidence-gathering pass — never trusting prior conversation as evidence. Turns each claim into a falsifiable check in a committed `.verify/*.json` file, runs it with a deterministic runner script (head vs base, test-tampering scan), and emits a verified/partial/refuted verdict with a reports/verify-*.md file. Use on `/verify`, before committing, or after any agent-driven change when you need to trust "done" rather than assume it.
argument-hint: "[task description or claims to verify]"
allowed-tools:
  - Bash
  - Read
  - Write
  - Glob
  - Grep
  - Task
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

**Judgment writes the checks; a script runs them and decides.** The agent's job is
to turn claims into checks that can fail. The runner script executes them, compares
head against base, scans for weakened tests, and computes the verdict from exit codes
and regexes alone. The same commit and checks file always give the same verdict, and
anyone can rerun it later without an agent.

The runner is `scripts/verify_run.py` next to this skill
(`~/.agents/skills/verify/scripts/verify_run.py`). Its end-to-end tests are
`tests/test_verify_run.py` in the same folder.

## Trigger

- Run on `/verify`, when asked to confirm that work is really done, and right before
  committing agent-driven changes.
- Treat the arguments as the claims/task description to verify.

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
(a) the feature behaves as described, (b) the full test suite passes.

### 2. Hand the claims to a fresh subagent

Use a fresh subagent if this environment offers one. Give it only the claims list
from step 1, the repo path, and steps 3–4 of this skill. Pass no conversation history,
no summary of the work, and no hint about what should pass. The subagent writes the
checks file and runs the runner; you relay its output. If no subagent is available, do
steps 3–4 yourself and pass `--independence inline` to the runner.

### 3. Write the checks file

Write `.verify/<task-slug>.json` at the repo root. If a `.verify/*.json` already
covers some of these claims, reuse its checks rather than writing new ones.

```json
{
  "task": "fix retry backoff",
  "claims": [
    {
      "id": "retry-fixed",
      "claim": "retry waits with exponential backoff",
      "run": "uv run pytest tests/test_retry.py::test_backoff -q",
      "fails_on_base": true,
      "base_fail_pattern": "AssertionError|1 failed"
    },
    {
      "id": "suite-green",
      "claim": "the full test suite passes",
      "run": "uv run pytest -q"
    },
    {
      "id": "csv-written",
      "claim": "export writes summary.csv with a total row",
      "run": "python -I .verify/checks/check_summary_csv.py out/summary.csv",
      "expect_output": "^total_rows=\\d+$"
    },
    {
      "id": "looks-right",
      "claim": "the settings page looks right",
      "run": null
    }
  ]
}
```

Fields: `id`, `claim`, `run` (required; a bash command run from the repo root, or
`null`); `expect_exit` (default `0`); `expect_output` (regex over combined
stdout+stderr); `timeout` in seconds (default 600); `fails_on_base` with its required
`base_fail_pattern`; `base_setup` (a command run in the base checkout first, such as
`npm ci`). Commands run in bash (Git Bash on Windows).

Write each check so it could actually fail:

- **Tests claimed to pass:** use the repo's real test command (check `README`,
  `package.json` scripts, `pyproject.toml`, `Makefile`, or CI config; do not guess
  `pytest` vs `uv run pytest` vs `npm test`).
- **Bug claimed fixed:** point `run` at the regression test and set
  `fails_on_base: true`. The runner checks out the base in a temporary worktree,
  copies in the new test files, and requires the check to fail there with output
  matching `base_fail_pattern`. The pattern names the failure that proves the bug,
  such as the assertion message, so a base that fails for an unrelated reason
  (missing dependencies, a syntax error) does not count. If no regression test
  exists, write one in the repo's test suite first.
- **Feature or behavior claimed:** run the feature, not `grep` the diff. A
  diff-presence check only fits a claim that is literally about the diff.
- **Artifact claimed created/updated:** a check that opens the file and asserts the
  claimed content, not just that it exists.
- **No existing command can falsify the claim:** write the smallest check script that
  can, under `.verify/checks/`, and point `run` at it. Keep it deterministic: fixed
  inputs, no network unless the claim is about the network, an assertion message that
  says what failed.
- **Truly unverifiable** (visual judgment, an external system you cannot reach): keep
  the claim with `"run": null`. The runner counts it as not reproduced. Never drop or
  reword a claim so it becomes easier to check.

### 4. Run the runner

From the repo root:

```bash
python -I ~/.agents/skills/verify/scripts/verify_run.py .verify/<task-slug>.json --independence subagent
```

Add `--base <ref>` only when the default base is wrong for this task. The runner:

- Picks the base: `HEAD` when tracked files have uncommitted changes, otherwise
  `git merge-base HEAD origin/<default-branch>`, falling back to `HEAD~1`. Untracked
  files never change the base (checks leave artifacts behind), so stage new files of
  uncommitted work (`git add -N <file>`).
- Runs every check on head, and the `fails_on_base` checks again on base.
- Flags existing test files that were deleted or lost lines since base (`tests/**`,
  `test_*`, `*_test.*`, `*.test.*`, `*.spec.*`, `conftest.py`).
- Computes the verdict:
  - **verified**: every claim reproduced and no test file flagged.
  - **partial**: at least one reproduced, but some claim was not reproduced, or a test
    file was flagged.
  - **refuted**: any claim contradicted (its check ran and failed), or none reproduced.
  - A timeout, exit 127, a `null` run, a check that also passes on base, or a base
    failure without `base_fail_pattern` all count as **not reproduced**. The runner
    fails closed.
- Records `head_sha`, `patch_id` (for uncommitted work), and `base` in the report. A
  verdict describes that exact code. After any new commit or edit, it is stale; rerun.
- Writes `reports/verify-YYYYMMDD-HHMM.md` and ignores `reports/` through
  `.git/info/exclude`, so the report never enters a commit and the working tree stays
  clean.
- Exits `0` verified, `1` partial, `2` refuted, `3` invalid checks file (fix the file
  and rerun).

If a check itself turns out to be wrong (a typo in the command, the wrong test path),
fix the check and rerun, and say what you changed in your reply. Changing an
expectation because the code doesn't meet it is weakening the check, not fixing it.

### 5. Report

Print the runner's stdout block verbatim:

```
VERDICT: {{verified|partial|refuted}}
CLAIMS_CHECKED: {{n}}
EVIDENCE:
- {{command}} -> {{status}}: {{reason}}
REPORT: reports/verify-YYYYMMDD-HHMM.md
```

Then one line saying the checks live in `.verify/<task-slug>.json` (plus any
`.verify/checks/` scripts) and belong in the same commit as the work: they are the
proof anyone can rerun with the command from step 4.

## Anti-Patterns

- Do not run `/verify` from the same context/session that did the work and rely
  on your own memory of having already run the tests — this skill's entire value
  is in re-executing checks, not recalling them.
- Do not override, soften, or reinterpret the runner's verdict. If you disagree,
  the disagreement belongs in a better check, then a rerun.
- Do not write checks that cannot fail: `echo ok`, `true`, a grep for a string the
  diff obviously contains, or a test that passes on base too.
- Do not skip claims because checking them is inconvenient. Use `"run": null`; an
  unchecked claim drives the verdict toward `partial`/`refuted`, never silently passes.
