---
name: apdeck
description: "Build or revise Allotrope-style PowerPoint decks from report content, template decks, or existing slides. Use when the user says /apdeck, asks for an Allotrope deck, wants highest adherence to an Allotrope template, needs a report turned into a branded PPTX, or wants a template-following slide workflow with rendered QA. Do NOT use for browser decks or generic presentations — use /present instead."
argument-hint: "[source-content | template-path] [--new|--revise]"
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - webfetch
  - Task
---

# apdeck

Build editable `.pptx` decks that follow an Allotrope template closely.

## When To Use

- `/apdeck` invoked explicitly
- Turn reports, memos, or HTML analysis into an Allotrope slide deck
- Review an existing Allotrope template and produce a new deck with high style adherence
- Revise an existing deck to conform more closely to Allotrope layout, branding, or slide rhythm

Do **not** use this skill for browser decks or generic presentations. Use `/present` instead when the user wants a non-Allotrope format or an HTML deck.

## Allotrope Style Guide

Read `references/pptx-allotrope.md` for the full brand specification (colors, fonts, slide templates, helper functions, QA workflow).

Key rules to remember even without the reference:

- Fonts: **Calibri Light** for headings and titles, **Calibri** for body — never Trebuchet MS
- Title slide background: `#1A5276`, section dividers: `#1B4F72`, content slides: `#FFFFFF`
- Green rule line under **every** content slide title (`#27AE60`, h: 0.04")
- Confidentiality footer on **every** non-title slide
- Stat card colors are semantic: green = favorable, red = unfavorable regardless of sign
- Slide dimensions: `LAYOUT_WIDE` (13.33" × 7.5")

## Workflow

### 1. Confirm Inputs

Identify before building:

- **Source content** — HTML reports, markdown memos, spreadsheet outputs, or a prior deck
- **Template deck path** — the `.pptx` template to follow
- **Output filename** — where to save the result
- **Job type** — `new deck`, `template-following rewrite`, or `targeted edit`

Defaults if the user is brief:

- Build a new `.pptx`
- Follow the supplied Allotrope template closely
- Save under the current workspace

### 2. Audit the Template

Always inspect the actual template deck before writing slides.

- Export slide PNGs from the `.pptx`
- Extract slide text from slide XML or PowerPoint COM
- Identify native slide patterns: cover, executive summary table, project info table, conclusions card grid, economics page, methodology page, next steps/risks, closing slide
- Record typography, color system, footer wording, logo treatment, table grammar, preferred content density

### 3. Write a Narrative Spine

Before editing slides, compress the source into a short slide list:

- title / kicker
- core claim
- proof object
- support note

If the source is a report, avoid dumping section headings directly onto slides. Reframe them into decision-oriented statements.

### 4. Build Strategy

Preferred order:

1. Edit from the real `.pptx` template (reuse native slide objects and positions)
2. Replace imported/merged tables with clean native tables when direct text edits break layout
3. Add new shapes only when the template does not already provide a compatible object

When PowerPoint COM is available on Windows:

- Use it to open, copy, edit, save, and export slide PNGs
- This is the best path for high-conformance template following

When a workspace already contains a deck builder script:

- Patch the builder
- Rerun it
- Inspect previews

### 5. Common Failure Modes

- Cover title becomes washed out because a new panel sits above the text
- Google Slides-imported tables keep merged-cell artifacts after text replacement
- Old template text remains underneath masked areas
- Footer gets clipped by new tables or panels
- Finance slides become too dense and lose the template's whitespace rhythm

Fix by:

- Deleting or masking original objects explicitly
- Rebuilding fragile tables from scratch
- Rerendering after every structural edit

### 6. QA Pass

Required checks before delivery:

- Cover slide looks intentional and readable
- Summary tables have no phantom rows and no old template text
- Card-grid slides fit in their tiles
- Economics slides preserve the Allotrope rhythm and footer
- Closing slide remains clean and branded
- No leftover placeholder text (search for lorem, ipsum, TODO, [insert, xxx)

## Output Rules

- Default output is a `.pptx`, not PDF
- Keep the deck editable
- Save the deck in the workspace unless the user specifies another location
- When asked for a desktop path on this machine, prefer `C:\Users\tukum\OneDrive\Desktop`

## Tooling

- **pptxgenjs** (npm) — creates `.pptx` from Node.js
- **markitdown** (pip) — extracts text for content QA
- **LibreOffice** (`soffice`) — converts `.pptx` to PDF for visual inspection
- **Poppler** (`pdftoppm`) — converts PDF to slide images

QA commands:

```bash
# Content check
python -m markitdown output.pptx

# Check for leftover placeholders
python -m markitdown output.pptx | grep -iE "\bx{3,}\b|lorem|ipsum|\bTODO|\[insert"

# Visual inspection
soffice --headless --convert-to pdf output.pptx
rm -f slide-*.jpg
pdftoppm -jpeg -r 150 output.pdf slide
```

## Validation

Before finishing:

- Open rendered slide previews
- Verify title slides, summary tables, finance slides, and closing slide visually
- Confirm no old template text remains under masks or replacement tables
- Confirm the deck path exists and the file opens cleanly