# /coop templates

Fill the `<...>` slots. `<run>` is the absolute path of `.coop/<slug>/`. `<you>` is `claude` or `agy`; `<peer>` is the other. `<DRIVER_PANE>` is your pane id.

## 00-brief.md

```markdown
# Coop: <slug>

Driver: <you> (pane <DRIVER_PANE>) · Peer: coop-<peer> · Started: <ISO date>
Root: <root> · Branch: <branch or n/a> · Task type: code | non-code

## Goal
<one or two sentences: the outcome, not the steps>

## Why
<what it is for, so trade-offs can be judged>

## Constraints
<stack, rules from CLAUDE.md/AGENTS.md/lessons.md that apply, limits>

## Out of scope
<what not to touch>

## Check
<the done predicate and how it is proven: commands, a run, or sources>

## Peer rules
- You are the coop peer. The driver does the editing. Write only inside <run> (repro scripts in <run>/scratch/), except during Execute (split mode or prose slices owned by you), when you may also edit exactly the files 02-plan.md assigns to agy/claude (you), and nothing else. Ask for changes to shared files in your report instead.
- Read the files each prompt names. Write the file it asks for, starting with the header line it gives.
- Run commands freely to gather evidence, but change nothing outside <run>: no edits, commits, pushes, installs, or PR comments. Do not start subagents.
- Your job is to make the result correct, not to agree. Back every finding with file:line, command output, or a source quote. Leave out what you did not check.
- Hold to the Goal. Other paths, rare cases, style, and small costs are nits.
- Last action of every turn, even on failure: run the report-back command the prompt gives, without --wait.
```

## ledger.tsv

Header row (tab-separated). Cells single-line; evidence is a pointer, not prose.

```
ts	phase	actor	decision	why	evidence	result
```

Example rows: `review r1	claude	fixed R2	null path crashed	src/a.ts:41, test b.spec	tests green`; `review r1	claude	disagree R3	caller already guards	src/c.ts:12	open`; `signoff	agy	score 9/10	-	08-summary.md	-`.

## Phase prompts

Every prompt ends with this report-back line (fill it per phase):

```
Last action: herdr agent prompt <DRIVER_PANE> 'coop-<peer> done: <phase> r<N> <result> <file>'
```

**Kickoff** (first prompt only, may be combined with Brainstorm):

```
Coop run. You are the peer; I am <you> in pane <DRIVER_PANE>. Read <run>/00-brief.md, especially Peer rules, and follow them for every prompt in this run.
```

**Brainstorm**

```
Brainstorm: read <run>/00-brief.md and the code or material it points to. Write <run>/01-ideas-<peer>.md starting with "# Ideas (<peer>)": 2-4 approaches, each with how it works, cost, main risk, and which you recommend and why. Do not read 01-ideas-<you>.md.
Last action: herdr agent prompt <DRIVER_PANE> 'coop-<peer> done: brainstorm r1 ok <run>/01-ideas-<peer>.md'
```

**Critique**

```
Critique r<N>: read <run>/00-brief.md and <run>/02-plan.md (and <run>/ledger.tsv for earlier rounds). Try to disprove the plan: wrong assumptions, missed callers or constraints, a simpler way, steps that do not meet the Check. Write <run>/03-critique-r<N>.md:
VERDICT: APPROVE or CHANGES
C1 [blocker|should|nit] <claim>. Evidence: <file:line / output / source>. Fix: <suggestion>
blocker = the Goal fails as planned. should = a real problem the Goal will hit. nit = the rest. For r2+, check only open ids and the changed plan.
Last action: herdr agent prompt <DRIVER_PANE> 'coop-<peer> done: critique r<N> <VERDICT> <run>/03-critique-r<N>.md'
```

**Checks** (sent at the start of Execute; `<base sha>` is the commit before any slice)

```
Checks: read <run>/00-brief.md and <run>/02-plan.md, not the code changes. Write <run>/04-checks.md starting with "# Acceptance checks": the commands (code) or claims to trace and numbers to recompute (non-code) that would prove the Goal and each slice, each with the expected result. Include at least one check that the original problem is gone. The pre-change code is base <base sha> (git show <base sha>:<path>); never use HEAD for the before state, since I commit slices while you write.
Last action: herdr agent prompt <DRIVER_PANE> 'coop-<peer> done: checks r1 ok <run>/04-checks.md'
```

**Build** (split Execute, or prose slices owned by agy)

```
Build: read <run>/02-plan.md. Build only your slices (owner: <peer>) and edit only the files listed for you there; I am building mine in the same tree at the same time. Do not commit, stage, format, or touch any other file, including lockfiles and shared config: list needed changes to those in your report. Run each slice's check. Write <run>/04-build-<peer>.md starting with "# Build (<peer>)": slices done, files changed, check commands with output, requested shared-file changes.
Last action: herdr agent prompt <DRIVER_PANE> 'coop-<peer> done: build r1 <PASS|ISSUES|BLOCKED> <run>/04-build-<peer>.md'
```

For prose slices, add to the Build prompt: `These slices are prose: write them with your unslop skill. If a fact-first draft exists at <file>, rewrite it in place and keep every number, date, name, link, quote, code span and footnote marker; add no facts. Audience: <...>. House voice: <...>.`

For slices with rendered output (deck slides, HTML pages, charts), add: `Render every slide or page you changed and look at each PNG yourself before reporting. Report PASS only if none shows clipped or overflowing text, stray line breaks, or overlapping shapes; list each PNG path with one line on what you checked.` (The 2026-11-25 Gap v0.81 build reported PASS with a clipped pill and broken lines in its own renders, which cost a fix round.)

**Review**

```
Review r<N> (read-only): base <sha or file list>. See git diff <base> plus untracked files (or the listed files), <run>/02-plan.md, <run>/ledger.tsv. Find bugs, broken callers, mismatch with the Goal, and code the Goal does not need. Skip style unless it hides a bug. Repo checks: <results>. Write <run>/05-review-r<N>.md:
VERDICT: APPROVE or CHANGES · SCORE: <n>/10
R1 [blocker|should|nit] <file>:<line> <claim>. Fix: <suggestion>
For r2+: the ledger shows fixed/disagree/declined; check open ids and code changed since r<N-1> only.
Last action: herdr agent prompt <DRIVER_PANE> 'coop-<peer> done: review r<N> <VERDICT> <run>/05-review-r<N>.md'
```

Non-code review: replace the diff with the document paths and look for unsupported claims, wrong numbers, missing counterpoints, and AI-sounding prose.

**Verify**

```
Verify r<N>: run every check in <run>/04-checks.md and the repo checks (<commands>) against the current tree. Write <run>/07-verify-r<N>.md:
RESULT: PASS | ISSUES | BLOCKED · SCORE: <n>/10
CONCERNS: <one line of remaining concerns, or none>
V1 <check> -> <command> -> <output excerpt> -> pass|fail
List every failure you can prove, not only the first. A failure without the exact command and output (or the source and quote) does not count. The pre-change base is <base sha>.
Last action: herdr agent prompt <DRIVER_PANE> 'coop-<peer> done: verify r<N> <RESULT> <run>/07-verify-r<N>.md'
```

## 08-summary.md

```markdown
# Coop summary: <slug>

Outcome: <one line>

## Proof
<command> -> <output excerpt>

## Scores
| Seat | Critique | Review r1 | Review r2 | Verify | Sign-off |
| --- | --- | --- | --- | --- | --- |
| <peer> | APPROVE | 7/10 | 9/10 | PASS 9/10 | 9/10 |
| <you> | - | - | - | - | 9/10 |

## Disputes and follow-ups
<open disputes; declined nits as follow-ups>

## Unverified
<what no check covered>
```
