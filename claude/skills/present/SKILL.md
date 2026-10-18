---
name: present
description: Build a presentation by editing a user-supplied template/ppt/pptx in place — preserve its real masters, layouts, logos, backgrounds, and diagrams, and replace the content at the existing shape positions with new text and rendered PNG charts/screenshots. Use whenever the user says /present, "make slides/deck from this template", "update last year's deck", "reskin this pptx", or gives an existing .pptx/.ppt to fill with new content. This produces an authentic continuation of the source deck, NOT a generated-looking from-scratch deck. For an Allotrope template use apdeck; with no template use the pptx skill.
user-invocable: true
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
---

# /present — Build a deck by editing a template in place

Arguments passed: `$ARGUMENTS`

## What this skill does (and why)

The default way to "generate slides" is to build a new deck from scratch with a
house template. That reliably looks **generated** — it cannot reproduce a
specific source deck's photographic title slides, hand-drawn vector diagrams,
exact brand masters, or logo placements.

This skill does the opposite: it **opens the user's actual template `.pptx` and
edits it**. The output *is* the original file with content swapped at the
existing shape coordinates, so it inherits 100% of the source's visual identity.
This is the preferred process — it directly solves the "generated-looking"
problem.

Use this skill **only** when there is a template/source deck to edit. If the
user truly wants a brand-new deck with no reference file, say so and offer the
managed generators (`anthropic-skills:pptx`, or a from-scratch `pptxgenjs`
build) instead.

Routing: an Allotrope template (or a request for an Allotrope-branded deck) goes
to `anthropic-skills:apdeck`. Any other supplied template stays here. No template
goes to `anthropic-skills:pptx`.

## Inputs to confirm before building

1. **Template file** — the `.pptx`/`.ppt` to edit (ask for the path if not given).
   If it's `.ppt`, convert to `.pptx` first:
   `soffice --headless --convert-to pptx <file>.ppt`.
2. **New content** — the text, numbers, and which slides change. Pull real
   values from the repo/source the user points to; never invent figures.
3. **Visual assets** — what goes in the image slots: rendered charts (matplotlib),
   app/screenshots, or existing images. Pre-render these to PNG.
4. **Output path** — default to a new filename next to the template; never
   overwrite the template itself.

## Procedure

### 1. Inventory the template
Run the inspector to learn each shape's index, id, name, type, geometry, and
current text on every slide. This map is the contract for every edit. **Target
shapes by `shape_id` or name**, not by a remembered index:

```
python "<skill_dir>/scripts/inspect_template.py" "path/to/template.pptx"
```

Read the output carefully. Note for each slide: which TEXT_BOX/PLACEHOLDER
holds the title, headline, and body; which PICTURE shapes are old content
images (to delete/replace) versus decorative brand assets (logos, rails,
backgrounds — **keep these**); and the slide size.

### 2. Pre-render the visual assets
Generate the PNGs the deck will drop into image slots (charts, tables,
equation cards, screenshots). Render at high DPI (≈220) on a white background so
they look crisp in the slide. Keep them in a dedicated asset folder.

### 3. Write the build script
Create a Python script using `python-pptx` that:
- Opens the template: `prs = Presentation(template_path)`.
- For text: replace runs **in the existing shape** (look it up by id or name). Reuse a
  `set_text(shape, text, size, bold, color, font, align)` helper that clears the
  text frame, zeroes margins, sets one run, and **suppresses any inherited
  bullet** (append `<a:buNone/>` to the paragraph's `pPr`) so reused
  bullet-formatted boxes don't render a stray bullet.
- For images: `delete_shape(old_picture)` then
  `slide.shapes.add_picture(png, Inches(x), Inches(y), Inches(w), Inches(h))`
  at the **same position** the original image occupied.
- For panels behind new content on dark areas: drop a white/grey rounded rect
  cover, then place stat cards / bullets on top.
- Saves to the output path (not the template).

Keep edits minimal and positional — match the original layout. Do not add slides
or restructure unless the user asks; this skill mirrors the source 1:1.

The reusable helpers live in `<skill_dir>/scripts/pptx_helpers.py`: `set_text`,
`suppress_bullet`, `add_textbox`, `add_bullets`, `add_stat_card`, `delete_shape`,
`add_picture_cover`, `replace_picture`, `cover`, `shape_by_id`, `shape_by_name`.
Import them (`sys.path.insert(0, "<skill_dir>/scripts")`) instead of rewriting them.

### 4. Build and QA — this step is mandatory
In-place edits keep the **original box sizes**, so replaced text frequently
overflows its box or collides with an image placed below it. You MUST render and
look:

```
python "<skill_dir>/scripts/render_deck.py" "output.pptx"
```

Then Read every slide PNG. Hunt specifically for:
- Headlines that now wrap to 2 lines and overlap the chart/table below them.
- Text spilling past the right edge or off the bottom.
- Stray/double bullets from reused list boxes.
- New cover panels not fully hiding old dark backgrounds.

Fix by reducing font size, nudging the image's `y`/height, or widening the box —
then rebuild and re-render the affected slides until clean. Treat the visual
render, not a successful save, as the definition of done.

### 5. Report
Tell the user the output path, slide count, what changed, and surface any
remaining judgment calls (e.g. "no live screenshot included — want one?").

## Common pitfalls
- **Don't delete decorative pictures by index blindly** — confirm a PICTURE is
  old content (chart/photo) before removing it; logos and rails are also PICTUREs.
- **Deleting a shape shifts the index of every later shape** in `slide.shapes`,
  original template shapes included. Target shapes by `shape_id` or name
  (`shape_by_id` / `shape_by_name`), or resolve every shape you need first and
  delete in descending index order.
- **Fonts**: match the template's fonts (inspect the master) so replaced text
  blends in.
- **Never overwrite the source template.** Always write a new file.
