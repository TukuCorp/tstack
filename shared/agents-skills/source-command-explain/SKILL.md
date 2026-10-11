---
name: source-command-explain
description: Explain a topic visually — either quick inline visuals (pseudocode, call/file trees, Mermaid, diffs) for the user, or a polished, grounded HTML explainer page for a named audience that knows little about the subject (clients, executives, partner teams, regulators, new joiners). Use when the user invokes `/explain`, or asks to "explain X to <team/person>", "make an explainer/one-pager/walkthrough page", "help <audience> understand how this works", or wants a process, method, system, model or analysis turned into something a non-technical reader can follow. Works for any domain — code, data pipelines, finance, science, policy, operations.
---

# Explain

Turn a topic into understanding. If a topic follows `/explain`, explain that;
otherwise explain the current topic of conversation.

## Step 0 — pick the mode

| Signal | Mode |
|---|---|
| The reader is the user, mid-task; "how does this work", "show me" | **Quick** — inline visuals in the reply |
| A named audience other than the user ("for the BIDV team", "for my CFO", "for new hires"), or "page", "html", "artifact", "one-pager", "share", "walkthrough" | **Explainer page** |
| Unclear | Quick, then offer the page in one line |

**Quick mode:** read `references/quick-views.md` and pick the smallest view that
makes the point. Skip the preamble. Stop there.

**Explainer page:** follow the workflow below. It exists because a page for an
outside audience fails in predictable ways: stale numbers, jargon, diagrams that
show the whole system instead of the reader's slice, and no clear ask. Each step
prevents one of those.

## Explainer-page workflow

### 1. Ground it in the current state, not in memory

"Given current progress" means the newest truth on disk, not the first plan.

- Find the most recent artifacts: outputs, review files, status notes, changelogs,
  dated reports. Sort by modified time; the newest file usually wins over an older
  summary page.
- Pull every number you will show from a primary file (spreadsheet, JSON, CSV, DB)
  with a short script, and keep a note of which file each number came from. Prior
  summary pages are a map to the facts, not the facts.
- Collect 4–6 concrete cases that span easy → hard, including at least one where
  the obvious answer was wrong. Real cases teach more than any rule statement.
- Note open items, pending decisions and dates — the reader usually needs to act.
- Anything you add from general knowledge rather than a file goes on a
  "please verify" list for the hand-off.

### 2. Profile the reader

Answer in one line each before writing: What do they already know? What decision
or action follows from reading? What must stay confidential or out of scope? What
language do they read in? (For non-English readers, add short native-language
subtitles to section headings — only where you are confident of the wording.)

### 3. Build the arc

Use this order; drop sections that do not earn their place. Detailed patterns for
each are in `references/page-sections.md`.

1. **Answer first** — title as a plain question/claim, one-sentence answer, status
   pills with a date, 3–4 key numbers.
2. **The problem, by analogy** — one everyday analogy (two dictionaries, two
   examiners, a recipe) plus a side-by-side of the real thing.
3. **Roles and boundaries** — who does what; what data stays where.
4. **The method** — one flow diagram plus numbered step cards in plain words.
5. **Worked examples** — interactive picker over the real cases, easy → hard,
   including the case that shows why the method exists.
6. **How to read the quality signals** — confidence levels, scores, flags: what
   each means and what the reader should *do* about it.
7. **Results** — simple bars, one stacked split; explain any statistic in a
   sentence ("agreement after removing luck").
8. **What we need from you** — decisions table, a decision-rule diagram, a
   tick-list of open questions, a timeline with "now" marked.
9. **Limits** — what it cannot do, in plain cards.
10. **Glossary** — collapsible, every term that survived into the page.
11. **Footer** — scope statement, sources, working files.

### 4. Write in near-controlled English

Aim about 80% of the way to ASD-STE100 (Simplified Technical English). Full rules
and before/after examples: `references/plain-english.md`. The core:
one idea per sentence, ≤20 words, active voice, present tense, common words,
define each term once at first use and then never vary it, numbers as digits,
instructions as imperatives.

### 5. Draw the diagrams

- Use Mermaid in `<pre class="mermaid">` for flows, processes, decision rules and
  chains. Lavish (if installed) turns each one into an editable Excalidraw
  whiteboard; elsewhere it renders as a normal diagram.
- Keep each diagram to ≤8 nodes with ≤5-word labels. Long chains go top-to-bottom
  (`flowchart TB`); left-to-right chains of 6+ nodes shrink to unreadable.
- Avoid subgraphs for small diagrams — they cramp the layout. Show the boundary
  in the caption instead, and colour *your* piece with a `classDef`.
- Use HTML/CSS (cards, bars, side-by-side) for comparisons and numbers, not Mermaid.
- Each diagram gets a one-line caption saying what to notice.

### 6. Style it

- Match the subject project's existing look first (look for sibling HTML pages,
  CSS variables, brand colours, fonts). Otherwise start from
  `assets/explainer-template.html`, which already has tokens, dark mode, mobile
  layout, the example picker, the checklist and Mermaid wiring.
- Give each actor/coder/option one stable colour and reuse it everywhere.
- One self-contained HTML file; CDN scripts only from jsdelivr/cdnjs/unpkg; fonts
  from Google Fonts. Browser storage only for per-viewer conveniences, wrapped in
  try/catch.

### 7. Verify like a reviewer

Open the page in a real browser (headless Chrome, Playwright, chrome-devtools,
whatever exists) and:

- confirm every `.mermaid` block produced an `<svg>` and there is no horizontal
  overflow;
- screenshot full-page in the theme the user uses and *look* at it — cramped or
  tiny diagrams are the usual defect; fix and re-check;
- click the interactive bits once;
- re-check every number against the source note from step 1.

### 8. Deliver

- Save the file in the project, next to the material it explains (or an
  `explain/` folder at the project root) — never only in a temp directory.
- Publish if the harness can: Claude Code `Artifact` tool (private by default —
  tell the user the audience cannot open it until they share it); `lavish-axi
  <file>` for annotation and Excalidraw editing; otherwise open it with the
  platform opener (`start ""`, `open`, `xdg-open`).
- Hand-off message: link + project path, the arc in one line per section, which
  design source you used, and the "please verify" list from step 1.
