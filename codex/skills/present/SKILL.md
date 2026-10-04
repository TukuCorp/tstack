---
name: present
description: "Turn any content into a polished presentation. Use when asked to `/present`, make slides, build a deck, create a presentation, present data, visualize material, or turn notes, research, data, or documents into a shareable visual format. Two modes: `html` for an interactive browser deck and `pptx` for an Allotrope-aligned PowerPoint. Infer mode from context when not specified."
---

# present

Convert any content — notes, data, research, documents — into a polished presentation.

## Mode Selection

| Situation | Mode |
|-----------|------|
| Formal deliverable, client-facing, needs a file | **pptx** |
| Internal review, browser-shareable, data/interactive | **html** |
| User says "html", "interactive", "browser" | **html** |
| User says "pptx", "powerpoint", "deck", "slides file" | **pptx** |
| Ambiguous | Ask: "HTML (interactive browser) or PowerPoint file?" |

---

## HTML Mode

Read `references/html-mode.md` for full instructions.

Single self-contained `.html` file with inline CSS/JS. Keyboard/click navigation, Chart.js for data, Mermaid for diagrams, CSS Grid layouts.

---

## PowerPoint Mode

Read `references/pptx-allotrope.md` for full instructions.

Allotrope-aligned `.pptx` via pptxgenjs. White backgrounds, Trebuchet/Calibri fonts, navy + green palette, financial stat callouts, confidentiality footer on every slide.

---

## Before Generating

Identify:
1. **Content source** — raw text, uploaded file, data tables, research?
2. **Audience** — internal Allotrope team, external partners, client?
3. **Length** — quick 5-slide overview or full 15-slide deck?
4. **Key message** — what should the audience walk away knowing?

Make reasonable defaults if unspecified; ask one focused question only if truly ambiguous.

---

## Output

Save the output file to the current working directory or a location the user specifies. Use a descriptive filename (e.g. `vida_wg_overview.html`, `vietnam_update.pptx`).
