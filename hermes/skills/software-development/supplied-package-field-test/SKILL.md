---
name: supplied-package-field-test
description: "Use when field-testing a package someone sent you."
version: 1.0.0
author: Hermes Agent
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [QA, Package-Validation, Field-Test, Report, Agent-Workspace]
    related_skills: [windows-cc-orchestration, vault-html-report, gws-workflows]
---

# Field-testing a supplied package

For when someone sends a tool, workspace or deliverable (a zip, a Drive link, a portable agent workspace) and the question is not "what does it say" but "can a real person actually run it, and where do they get stuck". The output is a findings list a non-technical owner can act on, not a code review.

Distinguish this from reading the docs: the whole point is executing the thing, in order, and recording what breaks.

## Phase order

1. **Pull and verify the package.** Get it from the source of record (email link, Drive), confirm the bytes match the source metadata, confirm the archive passes an integrity check, then extract into a gitignored folder named for sender and period. Write a `MANIFEST.md` (source id, file ids, sizes, layout, what it supersedes). Recipe: `gws-workflows` -> `references/gws-drive-export-download.md`.
2. **Read the package's own contract, end to end, before running anything.** The end-user guide, the entry-point doc, the setup doc, the process doc and the prompts file. Note the words it uses for status (Ready / Not ready / REVIEW_REQUIRED) so you can quote them back.
3. **Run the package's own self-checks first.** They are the fastest signal and they are the author's own definition of ready. Record every failing check by name and exit code.
4. **Prove the capability chain the guide claims is needed, yourself.** Typically: read a workspace file, write the document format, render it, read the render back, produce a page image. Record the artifact size at each step. This is what separates "the guide says it works" from "it works here".
5. **Drive the documented agent route**, one documented message per invocation, same session. Use the package's own prompts verbatim: paraphrasing loses the contract you are testing. Depth on invoking and resuming an agent CLI: `windows-cc-orchestration`. When a message runs for tens of minutes, arm an alert channel rather than polling blind, so you learn the moment each turn ends and can steer mid-run — the `herdr` skill carries a self-rearming watcher that detects completion from the agent's output instead of its status field.
6. **Collect findings and report.** Never overwrite a prior run folder, never modify the supplied inputs, and never author the deliverable unless asked. Inspecting is the job.

## Non-negotiables

- **Execute, do not opine.** A finding without a command and its output is a guess. Put the command and the observed result under every claim.
- **Re-test the agent's environment claims yourself before acting on them.** Agents running in a sandbox report environments as broken that work fine from your shell, then improvise workarounds worse than the tooling they bypassed. Confirm, then send the correction as a fact plus "do not replace the environment".
- **A script's PASS, exit code or printed verdict is not evidence of the work.** Exit 0 means the turn ended. Read the artifacts.
- **Recompute every recorded fingerprint yourself — a package's own validators check structure and internal consistency, never whether a recorded hash matches the file it names.** Invented digests are the one defect with no other symptom: a manifest full of them still reads as clean and every shipped checker still passes. Compare each recorded value to the file on disk, and check the LENGTH first — a SHA-256 that is not exactly 64 hex characters was never computed from anything. A value that matches the real digest for a prefix and then diverges was typed to look right, not truncated. Put the recompute into the acceptance message you send the agent; that is what actually catches it.
- **When the agent reports a fix, re-verify the artifact it names AND the sibling files carrying the same data.** A fix pass repairs the file its report mentions while leaving the identical defect in a second file that duplicates it, and the report still reads "rebuilt and verified". Check every file that restates the repaired value.
- **Count the real requirement surface from the artifact**, not from prose about it: headings plus tables in the actual template, pages and extractable characters in the actual evidence, formula and cached cells in the actual workbooks. Numbers stated in a guide are often the smaller cousin of the real thing.
- **Check evidence readability before trusting any "I read the files" claim.** Per-page extractable text, and the count of image-only pages, decide whether the task is possible for a text-only agent. Probe with pypdf per page; render image-only pages with `pdftoppm -png -r 150` and read them as images. Report the count (`7 of 7 pages image-only`), never infer readability from a filename.
- **Bound the reading load and say so.** If the package asks one session to read hundreds of pages plus thousands of spreadsheet cells, that is a planning finding, not a footnote, and it is the reason the authoring step may not fit in one context.
- **Treat the account ceiling as a hard gate for any long run.** Check what the setup step already cost before promising a multi-hour authoring run.

## Findings taxonomy

Give every finding a stable id and one of three levels, then sort by level so the owner reads the blockers first:

- **Blocker**: stops a real user from finishing the task (missing required tool, unreachable account ceiling, unreadable evidence with no fallback).
- **Defect**: a wrong, missing or contradictory instruction that costs an hour (a shipped folder the guide describes but does not contain, a documented check that hangs, the needed template version absent from the package).
- **Polish**: costs minutes (a flag the guide omits, numbering that skips a section).

One rule per finding, with the mechanism in a clause: `winget installs the tool but leaves the current shell's PATH stale, so an agent that installs then immediately re-checks reports failure with the tool present.` An environment failure you caused yourself by tightening a policy below the user's default gets labelled as your test condition, not as a package defect.

## Artifact hygiene

- Extract and run inside a folder the repo ignores (check `.gitignore`, do not assume).
- Keep the source archive beside the extraction, and prove it is untouched by re-hashing a sample against the package's own contents manifest when it ships one.
- When asked to delete the test scaffolding, delete only what you created: your scripts, logs, prompts, the virtualenv, run output folders, caches and generated report files inside the package. Re-hash a sample afterwards to show the delivered package is byte-identical, and tell the user which paths survived and why.

## The report

HTML, in the repo's existing `reports/` directory, following the house style already there (grep a recent file for `:root` and reuse its tokens and fonts). Structure that worked: masthead with source ids and a status chip, a KPI strip, a verdict box naming where it stopped and why, a run log with wall-clock times, an environment matrix of check-before and check-after, the capability chain as a figure, a platform-route table, findings as severity-striped cards, any decision matrix the contract demanded, an evidence table, an artifact inventory, reproduce commands, and an explicit "what this run did not do". Verify it in a browser before delivering: zero console errors, no horizontal overflow at desktop and narrow widths, component counts matching the source facts. Serve the reports directory (`python -m http.server <port>`) and drive it with the browser-control CLI, measuring `document.documentElement.scrollWidth` against `clientWidth` at a desktop and a phone width in the same script. In that pass also assert the DECLARED totals — the KPI strip and any "N findings" chip — against the DOM counts they summarise: a hand-written count drifts from the cards beneath it, and the masthead is the first number a reader checks. A wide table inside an `overflow-x:auto` wrapper legitimately extends past the viewport without overflowing the page, so judge overflow on `scrollWidth` vs `clientWidth`, not on which elements stick out. Full guidance: `vault-html-report`.

State the limits out loud. "It got through setup and inspection and stopped before authoring" is a result; a tidy page that implies more coverage is not.
