---
name: coop
description: Run one task end to end as a pair of agents, Claude Code and agy (Antigravity CLI), each on its default model, side by side in two panes of the same Herdr tab. The harness you invoke drives and does the editing (or splits disjoint files with the peer when the plan says so); the other is the peer that brainstorms in parallel, critiques the plan, reviews, and verifies. They hand off through files in `.coop/<slug>/` and report back by `hc send`, without polling. Full send by default, for code and non-code tasks. Use for `/coop`, "coop this", "pair with agy/claude on this", or a request to have Claude and agy work a task together. Needs herdr-core (`hc`, HC_TERMINAL_ID set). Not for fanning out to many agents (use necro) or a single cross-model review of an existing diff.
argument-hint: "<task>"
---

# Coop

Two agents finish one task together. You (the harness the user invoked) are the **driver**: you frame, plan, edit, fix, and report. The other harness is the **peer**: it works from files you name, writes inside the run folder (plus its own assigned files when the plan splits execution), and challenges your work. Each runs on its own default model; never pass a model flag.

| You are | Peer kind | Peer name | Your name in the ledger |
|---|---|---|---|
| Claude Code | `agy` | `coop-agy` | `claude` |
| agy | `claude` | `coop-claude` | `agy` |

The run is **full send**: no approval stops. You own it from the request to a verified result and a final report. The only reasons to stop early and ask the user are in "Stop and ask".

hc commands and gotchas: `references/hc.md` (next to this file). Brief, prompts, and report formats: `references/templates.md`. Read both before step 1.

## 0. Preconditions

1. `HC_TERMINAL_ID` must be set (for example `t5`). If not, say you are not in an hc terminal and stop. This address is where the peer reports back. Call it `DRIVER`.
2. Read your space and tab ids from your own labels (`references/hc.md`, "Who and where you are"); the peer's pane goes beside you in that tab.
3. Check quota for both sides: `quota-axi` (Claude) and `quota-axi --provider agy`. If either is under 15% with a reset after the run would end, say so in one line and continue only if the task is small.
4. Work root: the git top level if the cwd is in a repo, else the cwd. If on the default branch of a repo and the task changes code, create a branch `coop/<slug>` first.

## 1. Frame (driver)

Pick a short kebab-case `<slug>`. Create `<root>/.coop/<slug>/`, add `.coop/` to `.git/info/exclude` in a repo (do not edit `.gitignore`), and write:

- `00-brief.md` from the template: Goal, Why, Constraints, Out of scope, Check (the done predicate and how it is proven), Task type (`code` or `non-code`), and the Peer rules block copied verbatim.
- `ledger.tsv` with the header row from the template. Log one row per decision, round, fix, or dispute from here on.

## 2. Start the peer

Reuse a live agent named after the peer (`hc get coop-agy` or `coop-claude`) if it sits in your tab. If it does, send it the **kickoff** prompt (templates). Otherwise start the peer as your child in a split beside you, with `--cwd <root>` and the kickoff prompt in the launch command (exact commands in `references/hc.md`). The kickoff says who it is, the run folder, the Peer rules, and the report-back command. Confirm the model in its header line with `hc read <peer> --lines 0`. If the peer will not start after the fixes listed in `references/hc.md`, stop and report; never substitute a different agent or model.

Every prompt you send ends with the report-back line, so the peer sends to `DRIVER` when it finishes, even when it fails.

## 3. Phases

Each phase names its owner and its output file. "Hand off" means: send the phase prompt, then keep working on your own share or end your turn; the report-back arrives as a new message from `coop-<peer> done: ...`. On every report-back, read the named file before you act on it. A report-back with no file, or a file without the required header, counts as a failure: re-prompt once, then log a gap.

| # | Phase | Owner | Output |
|---|---|---|---|
| 1 | Brainstorm | both, in parallel | `01-ideas-<peer>.md`, `01-ideas-<you>.md` |
| 2 | Plan | driver | `02-plan.md` |
| 3 | Critique | peer | `03-critique-r<N>.md` |
| 4 | Execute | driver edits, peer writes acceptance checks (split: both build disjoint files) | changes; `04-checks.md` (split: `04-build-<peer>.md`) |
| 5 | Review | peer, read-only | `05-review-r<N>.md` |
| 6 | Fix | driver | ledger rows |
| 7 | Verify | peer runs checks | `07-verify-r<N>.md` |
| 8 | Sign-off | both | `08-summary.md` |

**1. Brainstorm.** Hand off the brainstorm prompt, then write your own `01-ideas-<you>.md` **before** you open the peer's file, so the two stay independent. Then read both, note where they agree (a strong signal) and where they differ, and pick an approach. If they diverge wildly, the brief is under-specified: sharpen `00-brief.md` and rerun once.

**2. Plan.** Write `02-plan.md`: the chosen approach and the rejected ones in one line each, thin vertical slices (each with files or sections touched and its own check), the risks, and an `Execution: single | split` line (see Execute; split also names each slice's owner and file list). Keep it to the smallest change that meets the Goal. The critique checks the split too: overlapping files or a hidden dependency between halves is a blocker.

**3. Critique.** Hand off the critique prompt. The peer tries to disprove the plan and returns `VERDICT: APPROVE|CHANGES` with findings `C1 [blocker|should|nit] ...`. Answer each finding in the ledger (`fixed`, `disagree` with evidence, or `declined` for nits and out-of-scope), update the plan, and rerun critique only while a blocker or should stays open. Limit: 2 rounds.

**4. Execute.** The plan's `Execution` line picks the mode; `single` is the default.

- **single** (default): hand off the checks prompt first: the peer reads the brief and plan and writes `04-checks.md`, the commands or source checks that would prove the Goal, without seeing your code. Meanwhile, build the plan slice by slice. After each slice, run its check; in a repo, commit each slice.
- **split** (same tree): choose it only when the slices fall into groups with **disjoint files** that can be built and checked on their own, and the work is big enough that doing them in parallel saves real time (roughly 3+ slices). Docs plus code, frontend plus backend, separate modules, or sections of a document are typical. In `02-plan.md`, give every slice an owner (`claude` or `agy`) and list the exact files each owner may touch; files neither owner lists are yours. Shared files (lockfiles, package manifests, a shared index or config) stay yours: the peer asks for a change to them in its report instead of editing. Hand off the build prompt (templates), then build your own slices. Neither side commits during split: you review the peer's changes with `git diff -- <its files>`, run the full checks, and commit once both halves are in. If the peer touched a file outside its list, revert that hunk and log it. Then write `04-checks.md` yourself, or hand the checks prompt to the peer before review.

Outside split mode, and outside its own listed files during split, the peer never edits outside `.coop/<slug>/`.

**5. Review.** When every slice is in, run the repo's checks, then hand off the review prompt with the base (`git merge-base HEAD <default branch>` or, outside git, the file list). Stage files by name, never `git add -A`: generated files (bytecode, build output) slip in otherwise. Do not edit while the peer reviews. Findings use `R1 [blocker|should|nit] <file>:<line> <claim>. Fix: ...`.

**6. Fix.** For each finding, check it yourself: agree, make the smallest fix and log `fixed`; disagree, log `disagree` with file:line or command output; nit or out of scope, log `declined` in one line. Do not agree just to end the loop. If the fixes grew the diff, cut before the next round. Rerun review only while a blocker or should is open or behavior changed. Limit: 3 rounds (5 for security, auth, permissions, data loss, or concurrency).

**7. Verify.** Hand off the verify prompt: the peer runs `04-checks.md` plus the repo's checks against the current tree and returns `PASS | ISSUES | BLOCKED`. A finding counts only with the exact command and its output (code) or the source and quote (non-code). On `ISSUES`, rerun each failing command yourself, fix the real ones, and verify again. Limit: 2 rounds; a check still failing after that goes in the report as open.

**8. Sign-off.** The peer's sign-off is the `SCORE` and `CONCERNS` lines of its last passing verify file; no extra round. Rerun the main check yourself and give your own score. Write `08-summary.md`: what was done, proof (commands and outputs), per-round scores table, disputes, declined items as follow-ups, and anything unverified. If a PR exists, put the scores table in its description. Then, if you started the peer in this run, end it (`references/hc.md`, Clean up); leave a reused peer running. Give the user the final report.

## Writing goes to agy

agy's default model (Gemini 4 Neon) is the better writer, so agy writes the words of every prose deliverable: emails and comms, docs and READMEs, reports and memos, artifact and slide copy, PR descriptions. Claude owns facts, structure, and code.

- **agy drives:** it writes the prose itself; Claude reviews it for facts and gaps.
- **Claude drives:** mark each prose slice `owner: agy` in `02-plan.md` (files listed, as in split mode; this is allowed even with `Execution: single`). Send the build prompt for those slices. Before that, you may write a fact-first draft: an outline with every number, source, and decision. If you do, agy rewrites it with its unslop skill instead of starting from nothing. Either way, run `fact_guard.py` from your unslop skill (`scripts/fact_guard.py <draft> <final>`) on the result, and fix any dropped or added facts yourself.
- Review and verify stay as above. The peer that wrote the prose does not verify its own facts: when agy wrote it, Claude checks every claim against the sources in Verify.

## Non-code tasks

Research, docs, decks, memos: the same phases, with these swaps. The "slices" are sections. The Check is the reader's question answered with every factual claim cited to an original source. Review looks for unsupported claims, wrong numbers, missing counterpoints, and AI-sounding prose. `04-checks.md` lists claims to trace and numbers to recompute; Verify opens each source and quotes the line that supports or contradicts the claim. The prose itself is agy's, per "Writing goes to agy"; the final text still gets the mechanical check from the unslop skill.

## Rules

- **One writer per file.** By default only you edit files outside `.coop/<slug>/`; in split mode, and for prose slices owned by agy, the peer also edits exactly the files the plan assigns it, during Execute only. Never both on one file. The peer may keep repro scripts in `.coop/<slug>/scratch/`. Review, fix, and verify always run with you as the only writer.
- **Files carry content, prompts carry pointers.** Keep each prompt to a few lines naming the files to read and the file to write.
- **No polling loops.** Hand off, then do your own share or end your turn. The report-back wakes you. If you need to check on the peer, one `hc get <peer>` plus `hc read <peer> --lines 0` is enough.
- **Fight scope creep.** Hold every round to the Goal. A finding about a different path, a rare case, or a small cost is a nit.
- **No substitution.** If the peer is down, stop and report; do not continue alone and call it a coop.
- **Ledger, not memory.** Every round, verdict, score, and dispute goes in `ledger.tsv`. Never invent a score; write `no score`.
- **Disputes.** You decide, with evidence. A blocker the peer raises twice that you still reject goes into the final report as an open dispute.

## Stop and ask

Full send covers the task's own edits and checks. Stop and ask the user only for: production or shared-resource changes, data deletion, pushes to a default branch, spending money, sending messages to people, a peer that will not start, or a Goal that turns out to be contradictory.

## Final report

Lead with the outcome, then: the run folder path, proof (command and output), the scores table, open disputes and follow-ups, and what stayed unverified. Keep it short.
