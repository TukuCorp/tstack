---
name: apdeck
description: "Build or revise Allotrope-style PowerPoint decks from report content, template decks, or existing slides. Use when the user says `/apdeck`, asks for an Allotrope deck, wants highest adherence to an Allotrope template, needs a report turned into a branded PPTX, or wants a template-following slide workflow with rendered QA."
---

# apdeck

Build editable `.pptx` decks that follow an Allotrope template closely.

## When To Use

Use this skill when the task is any of:

- `/apdeck`
- turn reports, memos, or HTML analysis into an Allotrope slide deck
- review an existing Allotrope template and produce a new deck with high style adherence
- revise an existing deck to conform more closely to Allotrope layout, branding, or slide rhythm

Do not use this skill for browser decks or generic presentations. Use `$present` instead when the user wants a non-Allotrope format or an HTML deck.

## Workflow

1. Identify the source content, template deck, desired output path, and whether the user wants a new deck or a revision.
2. Audit the template before building. Extract slide text, render slide PNGs, and note the native slide types you should preserve.
3. Write a short claim spine for the new deck before editing slides. Keep each slide conclusion-led.
4. Prefer editing from the actual `.pptx` template when PowerPoint COM automation is available. Reuse native slide geometry instead of redrawing approximate layouts.
5. If a workspace already contains a deck builder script, extend it rather than starting over. In the `reopt-pysam` repo, prefer `scripts/build_case3_allotrope_deck.ps1` as the pattern for template-driven deck generation.
6. Render slide previews after export and fix overflow, clipping, broken tables, washed-out title text, and leftover template artifacts before delivery.

Read `references/workflow.md` for the detailed checklist and validation rules.

## Output Rules

- Default output is a `.pptx`, not PDF.
- Keep the deck editable.
- Save the deck in the workspace unless the user specifies another location.
- When asked for a desktop path on this machine, prefer `C:\Users\tukum\OneDrive\Desktop`.

## Repo-Specific Notes

For `C:\Users\tukum\Downloads\reopt-pysam`:

- template source used so far: `reports/decks/conformance/template/allotrope-template.pptx`
- finished deck pattern: `reports/decks/*.pptx`
- conformance references: `reports/decks/conformance/*.md`
- existing builder example: `scripts/build_case3_allotrope_deck.ps1`

## Validation

Before finishing:

- open rendered slide previews
- verify title slides, summary tables, finance slides, and closing slide visually
- confirm no old template text remains under masks or replacement tables
- confirm the deck path exists and the file opens cleanly
