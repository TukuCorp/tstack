# AP Deck Workflow

Use this reference only after `$apdeck` triggers.

## 1. Inputs To Confirm

- source content files: HTML reports, markdown memos, spreadsheet outputs, or prior deck
- template deck path
- output deck filename
- whether the job is `new deck`, `template-following rewrite`, or `targeted edit`

Default assumption if the user is brief:

- build a new `.pptx`
- follow the supplied Allotrope template closely
- save under the current workspace

## 2. Template Audit

Always inspect the actual template deck before writing slides.

Recommended checks:

- export slide PNGs from the `.pptx`
- extract slide text from slide XML or PowerPoint COM
- identify native slide patterns:
  - cover
  - executive summary table
  - project/case information table
  - conclusions card grid
  - economics page
  - methodology/detail page
  - next steps / risks
  - closing slide

Record:

- typography and color system
- footer wording
- logo treatment
- table grammar
- preferred content density

## 3. Narrative Spine

Before editing slides, compress the source into a short slide list:

- title / kicker
- core claim
- proof object
- support note

If the source is a report, avoid dumping section headings directly onto slides. Reframe them into decision-oriented statements.

## 4. Build Strategy

Preferred order:

1. edit from the real template deck
2. reuse native slide objects and positions
3. replace imported/merged tables with clean native tables when direct text edits break layout
4. add new shapes only when the template does not already provide a compatible object

When PowerPoint COM is available on Windows:

- use it to open, copy, edit, save, and export slide PNGs
- this is the best path for high-conformance template following

When a repo already has a deck builder:

- patch the builder
- rerun it
- inspect previews

## 5. Common Failure Modes

- cover title becomes washed out because a new panel sits above the text
- Google Slides-imported tables keep merged-cell artifacts after text replacement
- old template text remains underneath masked areas
- footer gets clipped by new tables or panels
- finance slides become too dense and lose the template’s whitespace rhythm

Fix by:

- deleting or masking original objects explicitly
- rebuilding fragile tables from scratch
- rerendering after every structural edit

## 6. QA Pass

Required checks:

- cover slide looks intentional and readable
- summary tables have no phantom rows and no old template text
- card-grid slides fit in their tiles
- economics slides preserve the Allotrope rhythm and footer
- closing slide remains clean and branded

## 7. Deliverables

Return:

- final `.pptx` path
- builder script path if you created or updated one
- any important assumption, especially if the template required masking or table reconstruction
