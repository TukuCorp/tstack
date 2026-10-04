---
name: present
description: Turn any content into a polished presentation. Use when asked to /present, "make slides", "build a deck", "create a presentation", "present this data", "visualize this", or any time notes, research, data, or documents should become a shareable visual format. Two modes: html (interactive browser deck) and template (edit an existing .pptx in place, preserving its masters, layouts, logos, and backgrounds). Infer mode from context when not specified.
---

# present

Convert any content — notes, data, research, documents — into a polished presentation.

## Mode Selection

| Situation | Mode |
|-----------|------|
| User supplies an existing .pptx/.ppt to edit/update | **template** |
| Internal review, browser-shareable, data/interactive | **html** |
| User says "html", "interactive", "browser" | **html** |
| User says "template", "edit this deck", "update last year's deck" | **template** |
| User says "pptx", "powerpoint", "deck", "slides file" | **apdeck** (use `/apdeck` instead) |
| Ambiguous | Ask: "HTML (interactive browser) or edit an existing template?" |

---

## HTML Mode

Read `references/html-mode.md` for full instructions.

Single self-contained `.html` file with inline CSS/JS. Keyboard/click navigation, Chart.js for data, Mermaid for diagrams, CSS Grid layouts.

---

## Template Mode (edit existing .pptx in place)

Edit the user's actual template `.pptx` and replace content at existing shape positions. The output inherits 100% of the source's visual identity — masters, layouts, logos, backgrounds, diagrams all preserved.

Use this mode **only** when there is a template/source deck to edit. If the user wants a brand-new deck with no reference file, use PowerPoint Mode or HTML Mode instead.

### Inputs to confirm before building

1. **Template file** — the `.pptx`/`.ppt` to edit (ask for the path if not given).
   If it's `.ppt`, convert to `.pptx` first:
   `soffice --headless --convert-to pptx <file>.ppt`.
2. **New content** — the text, numbers, and which slides change. Pull real
   values from the repo/source the user points to; never invent figures.
3. **Visual assets** — what goes in the image slots: rendered charts (matplotlib),
   app/screenshots, or existing images. Pre-render these to PNG.
4. **Output path** — default to a new filename next to the template; never
   overwrite the template itself.

### Procedure

#### 1. Inventory the template
Run the inspector to learn the exact shape index, type, geometry, and current
text of every slide. **Shapes are targeted by index**, so this map is the
contract for every edit:

```
python "<skill_dir>/scripts/inspect_template.py" "path/to/template.pptx"
```

Read the output carefully. Note for each slide: which TEXT_BOX/PLACEHOLDER
holds the title, headline, and body; which PICTURE shapes are old content
images (to delete/replace) versus decorative brand assets (logos, rails,
backgrounds — **keep these**); and the slide size.

#### 2. Pre-render the visual assets
Generate the PNGs the deck will drop into image slots (charts, tables,
equation cards, screenshots). Render at high DPI (~220) on a white background so
they look crisp in the slide. Keep them in a dedicated asset folder.

#### 3. Write the build script
Create a Python script using `python-pptx` that:
- Opens the template: `prs = Presentation(template_path)`.
- For text: replace runs **in the existing shape** at its index. Reuse a
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

#### 4. Build and QA — mandatory
In-place edits keep the **original box sizes**, so replaced text frequently
overflows its box or collides with an image placed below it. You MUST render and
look:

```
python "<skill_dir>/scripts/render_deck.py" "output.pptx"
```

Then read every slide PNG. Hunt specifically for:
- Headlines that now wrap to 2 lines and overlap the chart/table below them.
- Text spilling past the right edge or off the bottom.
- Stray/double bullets from reused list boxes.
- New cover panels not fully hiding old dark backgrounds.

Fix by reducing font size, nudging the image's `y`/height, or widening the box —
then rebuild and re-render the affected slides until clean. Treat the visual
render, not a successful save, as the definition of done.

#### 5. Report
Tell the user the output path, slide count, what changed, and surface any
remaining judgment calls (e.g. "no live screenshot included — want one?").

### Common pitfalls
- **Don't delete decorative pictures by index blindly** — confirm a PICTURE is
  old content (chart/photo) before removing it; logos and rails are also PICTUREs.
- **Indices shift after deletion only within your own added shapes**, not the
  original ones you read — but re-inspect if behavior surprises you.
- **Fonts**: match the template's fonts (inspect the master) so replaced text
  blends in.
- **Never overwrite the source template.** Always write a new file.

---

## Before Generating

Identify:
1. **Content source** — raw text, uploaded file, data tables, research?
2. **Audience** — internal team, external partners, client?
3. **Length** — quick 5-slide overview or full 15-slide deck?
4. **Key message** — what should the audience walk away knowing?

Make reasonable defaults if unspecified; ask one focused question only if truly ambiguous.

---

## Output

Save the output file to the current working directory or a location the user specifies. Use a descriptive filename (e.g. `vida_wg_overview.html`, `vietnam_update.pptx`).
