---
name: teach-workspace-authoring
description: Use when authoring or maintaining teach-workspace lessons.
---

# Teach Workspace Authoring

Companion to the generic `teach` skill (which is user-authored and cannot be patched — this is
the operational layer for the MIT OCW study workspace at `<PRIVATE_REPO>/teach-workspace/`:
EE power/energy core + SE track, 12-14h/wk, 8-week Phase 1, dual-track).

## Workspace contract (enforced by `tools/verify_workspace.py`)
- Required files: MISSION.md, RESOURCES.md, GLOSSARY.md, NOTES.md, PROGRESS.md, LESSON-MAP.md,
  assets/style.css, assets/quiz.js, tools/verify_workspace.py
- Lessons: `lessons/NNNN-<kebab-slug>.html` — contiguous from 0001, number = max(existing)+1 at
  authoring time. **Check LESSON-MAP.md before authoring** — rows carry the intended study order.
- Per-lesson requirements (verifier checks): link `../assets/style.css`, contain "Primary
  source", link `../MISSION.md`, contain `<section class="quiz">`.
- Learning records: `learning-records/NNNN-<slug>.md`, contiguous from 0001.
- After any authoring or merge run:
  `python teach-workspace/tools/verify_workspace.py teach-workspace` plus the tool's unit tests.
- Verifier pitfall: run it from the repo ROOT with the workspace arg as shown. Invoking
  `tools/verify_workspace.py` from inside `teach-workspace/` with no arg makes the workspace default
  to `teach-workspace/teach-workspace` — every required file then reports as missing (a spurious
  FAIL that looks like data loss; it is a cwd problem, not a workspace problem).
- Full markup contract: `references/lesson-html-contract.md`.

## Quiz authoring rules (hard)
- All options in a question must have the SAME word count — formatting must never hint at the
  answer. (Caught twice in real use: unequal options, and all-correct-at-index-0 — both are clues.)
- Shuffle correct-answer positions across questions; never repeat one index pattern.
- Correct option gets `data-answer="true"`, distractors `"false"`; explanation in
  `<p class="explain">` (revealed after answering via the `.answered` class).
- Ground examples in the user's domain (BESS controller state machines, knapsack portfolio
  selection) in a callout near the top — mission tie first.
- The repo verifier does NOT check these rules — run `scripts/quiz_audit.py` (this skill)
  after authoring: flags unequal option word counts, option counts != 4, missing/duplicate
  correct answers, and repeated correct-index patterns. Pre-existing violations in
  0003/0008/0009 predate the rule (found 2026-09-04); fix only lessons you authored.

## Opening lessons on this machine
- `explorer.exe <file>` opens a file-explorer window on this machine (observed 2026-08-30: exits 1, no browser). For local `file://` lessons the working open is `cmd.exe /c start "" "C:\...\lessons\NNNN-slug.html"` — launches the default browser at a `file://` URL (verified 2026-08-30 for 0007-0009). `cmd //c start "" <file>` (double-slash) is the wrong form on MSYS — use single-slash `cmd.exe /c start`. Do not use `computer_use` for browser work — the user's standing correction is browser-control only (2026-08-28).
- GitHub Pages (private-repo 422): `tah-allotrope/<PRIVATE_REPO>` is PRIVATE and free-plan Pages
  returns `422 Your current plan does not support GitHub Pages for this repository` for both
  standard-track and gap-ee (verified 2026-08-30 via `gh api .../pages --jq .has_pages`). Standard-track
  lessons still carry intended `https://tah-allotrope.github.io/<PRIVATE_REPO>/teach-workspace/lessons/NNNN-slug.html`
  links (forward-reference); they resolve only after the repo is made public or a public slice is
  pushed. For gap-ee week 1 the workaround was a public slice repo `gap-ee-week1` (see
  `references/github-pages-week1.md`). The same slice pattern applies to standard-track if sharing
  before the main repo is public.
- Standard track (`teach-workspace/lessons/*.html`): `browser-control execute
  'await page.goto("file:///C:/Users/tukum/Downloads/<PRIVATE_REPO>/teach-workspace/lessons/0001-foo.html")'`
- Gap-EE track (`teach-workspace/gap-ee/lessons/*.html` + `gap-ee/artifacts/*.html`):
  must be served via HTTP — `file://` breaks asset loads (`../assets/style.css`,
  `../assets/quiz.js`). Serve the workspace root:
  `python -m http.server 8011 --directory "C:/Users/tukum/Downloads/<PRIVATE_REPO>/teach-workspace"`
  then
  `browser-control session new gap-ee-week1` +
  `browser-control execute --session gap-ee-week1 'await page.goto("http://127.0.0.1:8011/gap-ee/lessons/0001-thermo-and-heat-transfer-primer.html")'`
  — `context.newPage()` in one execute block opens several tabs; the session persists
  (`--session <id>` for follow-ups). `browser_exec`/cloud browser blocks
  `127.0.0.1` (`Blocked: URL targets a private or internal address`) — use
  browser-control only.
- Scope correctly when the user says "first week": gap-ee week 1 = 0001-0005
  (0001 thermo day1, 0002 refrigeration 1-2, 0003 steam 2-3, 0004 MEASUR 3-4,
  0005 TEA 5); week 2 = 0006-0011. Do not open 0006-0011 when only week 1 was
  asked. See `references/gap-ee-local.md`.
- Verify the widget initialized: `section.quiz li.q` count > 0 and `.quiz-score` exists.
  For gap-ee also `snapshot()` should show the gap-ee meta header
  (`gap-ee week 1, day …`) and activeTargets equals tab count.

## Markdown pane companions (user preference)
- The user reads lessons in herdr terminal panes: author `lessons/NNNN-<slug>.md` companions
  rendered from the canonical HTML (headings, code blocks, quiz with bolded answers, primary
  source). Render with `glow <file>` or `bat -l md <file>`.
- The verifier ignores non-.html files in lessons/, so companions are safe there.
- Regenerate companions from the canonical HTML when the HTML changes — never let them drift.

## Remediation / open-item review lessons
- When the user asks for a "report/guide" on open items (review of an unchecked checklist item),
  deliver it as a normal workspace lesson — verifier-passing HTML, interactive quiz, md companion —
  never a loose untracked file. Number it max(existing)+1 like any lesson; add rows to LESSON-MAP.md
  (week = the week of the items it remediates) and the PROGRESS.md authored table.
- Structure: lede naming the open item(s) + the pass bar; mission-tie callout; one section per
  missed topic, re-teaching the EXACT missed question first with worked numeric examples; a numbered
  "re-sit protocol" (re-read source → re-sit from memory → pass bar → log result in the learning
  record); practice quiz at diagnostic difficulty with FRESH questions (never the diagnostic's own
  items verbatim). Canonical example: `lessons/0006-dicts-and-comprehensions-review.html`.
- Do NOT tick the user's checklist item on your own authority — the lesson prepares, their actual
  re-sit score earns the tick. Put an ask-callout at the bottom ("report your score and I'll close
  it") and leave the checkbox alone until they do.
- Remediation lessons recur by design (PROGRESS.md week-6 buffer: re-sit any exam scoring below
  70.0), so this is a standing pattern, not a one-off.

## Concurrent agent sessions (user runs multiple herdr panes on the same repo)
- Expect collisions: another pane may scaffold/author/commit the same workspace while you work.
  Symptoms: `git log` shows foreign commits; `git show --stat <sha>` reveals its files; your
  writes land on top of its tracked files (git status shows them as M with your content).
- Reconcile, don't clobber: restore the other session's canonical version with
  `git checkout HEAD -- <paths>`; merge docs (MISSION/RESOURCES/NOTES) by combining unique
  content instead of overwriting; adopt its established conventions (markup contract, verifier
  tooling) over your own when it already has them in place.
- Record an ownership split in NOTES.md (e.g. "concurrent pane owns authoring/week execution,
  this pane owns review/tracking/markdown") and defer to the owner on shared files.
- Commit small non-conflicting deltas (new companion files, tracker rows) rather than
  re-writing shared files — repeated overwrites become thrash the user dislikes.

## Upstream workflow notes
- The research/ brainstorm file feeds the lesson map: when `/brainstorm` is re-invoked for a
  subject that already has a draft (e.g. an `--auto` run), treat its DEC-xxx entries as the
  interview defaults, mark each outcome (confirmed)/(REVISED) vs the draft, and note the
  superseded file — don't re-ask from scratch.
- `plans/` holds the `/plan` output (week-by-week spec); PROGRESS.md mirrors it as checklists.

## See also
- `references/lesson-html-contract.md` — exact quiz markup + verifier checklist
- `scripts/quiz_audit.py` — fairness audit the verifier skips (word counts, 4 options, one answer, index shuffle)
- `references/github-pages-week1.md` — free github.io for gap-ee week 1 (private-repo 422 workaround, public gap-ee-week1, Pages enable + browser-control open)
- `references/github-pages-standard-track.md` — standard-track github.io links (422 on private <PRIVATE_REPO>, file:// open via cmd /c start, slice alternative)
- The generic `teach` skill (pedagogy, MISSION grounding, ZPD, retrieval practice)
