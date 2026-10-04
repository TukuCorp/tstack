---
name: architectural-layout-studies
description: "Use when proposing room/floor layout options from a plan."
version: 1.0.0
metadata:
  hermes:
    tags: [architecture, layout, drawings, plans, svg, house]
    related_skills: [ocr-and-documents, excalidraw]
---

# Architectural layout studies

Producing **scaled 2D layout options** for a room or floor of a real building from
an existing contract drawing or compiled model ("divide this bedroom into a
bedroom + workspace", "re-plan this floor"). The user is the client here; the
architect is not in the loop.

The project for this on this machine: `C:/Users/tukum/Downloads/freecad-blender`,
house specs in `designs/`, contractor sheets in `contractor/`, deliverables in
`reports/`.

Not this skill: general PDF text extraction (`ocr-and-documents`), and the
spec-to-render pipeline itself — that is documented in the repo's own `AGENTS.md`
and `.claude/skills/homedesign/SKILL.md`; read those in the repo, do not restate
or contradict them here.

## Procedure

1. **Collect the three sources and treat them as possibly-disagreeing.** The
   contractor sheet (`contractor/MB *.pdf`) is the contract and wins on disputes;
   the compiled model (`designs/<slug>.json`, `output/compiled/<slug>.model.json`)
   gives plot, core, stair and lobby positions; `designs/<slug>.measurements.md`
   records what a previous session measured.
2. **Read the drawing properly** — rasterise and read the printed numbers with
   vision, then confirm against the vector linework. Recipe and commands:
   `references/reading-measured-plans.md`. Printed text layers are usually empty
   on these sheets, so `get_text()` returns nothing and OCR has nothing to chew.
3. **Audit the reconstruction as a SEQUENCE, not a set.** Walk the printed
   dimension chain band by band from a fixed datum (the street wall or the rear
   wall) and compare the order with the model's room list. A dump can name every
   room correctly and still have two adjacent bands swapped — presence checks
   pass, the 3D render is wrong, and every downstream drawing inherits it.
4. **Write the constraint line down before designing anything.** One sentence,
   e.g. "daylight is at the street end and the single entry is at the core end".
   This is what makes the options differ for a reason instead of at random, and it
   is the sentence the user is really choosing against.
5. **Draw four option archetypes.** They generalise across rooms: (a) front/rear
   split with a stud wall, (b) side split, front-to-rear, so each zone can have
   its own door, (c) a glazed box at the entry/core end, (d) no wall at all — bed
   placed, one track curtain. Four is enough contrast and still comparable on one
   sheet; two looks like a binary, six cannot be read side by side.
6. **One sheet, one scale, real geometry.** All four panels at the same scale over
   the as-drawn base, plus a separate as-drawn base sheet with dimension chains.
   Production recipe and a working generator: `references/option-sheet-production.md`
   and `templates/panel_plan_sheet.py`.
7. **Self-review the rendered sheet with vision before delivering** — half-crops,
   defect-only checklist (see the reference). Expect ~2 passes and one false
   positive per pass.
8. **Deliver files on disk with absolute paths** (plain-text CLI — no MEDIA tags),
   plus a compact chat summary: per option, its m², what it wins, and a `Costs:`
   clause. The cost line is what the user actually chooses on.
9. **Ask the decisions in ONE clarify batch**, recommended choice first: which room
   or space, how each side gets used, which option to develop, and whether to fix
   any discrepancy found. Never scatter these across turns.
10. **Stop at 2D.** Only after the user picks: author a spec variant under
    `designs/`, run `homedesign plans` for SVG/DXF, then `homedesign build` for the
    EEVEE preview and viewer.

## Standing preferences (this user)

- **Options first, drawn, with real areas in m².** State each option's cost; do not
  sell one. He picks after seeing the comparison, not from a description.
- **2D is the deliverable, not a waypoint.** "Stop at 2D for now" is the default
  expectation — a layout study ends with drawings and a question, not a render.
- **Keep the drawing's Vietnamese room labels on the plan** (P.NGỦ, BAN CÔNG, WC,
  LÔ GIA, TẦNG n) and write the captions, README and chat in English.
- **Never silently fix a model-vs-sheet mismatch.** Surface it with the evidence,
  offer the fix, let him decide — "leave it for now" is a valid answer and not a
  pending to-do to re-raise every session.
- **Reuse his vocabulary**: tầng (floor), lọt lòng (clear internal), ban công, lô
  gia, P.NGỦ. He reads the numbers in mm as printed (3560, 900, 1400).
- **Deliverables live in the repo** under `reports/<date>-<topic>/`, with the
  generator script beside the outputs so any option can be re-rendered after a
  one-line edit. Name the folder for the subject, not the first guess at it — if
  the target room changes, rename rather than nesting a second set.

## Pitfalls

- **"The bigger bedroom" / "the other room" is ambiguous and can be a 100 mm
  difference.** Printed clear areas of two rooms can differ by under 0.2 m², so a
  comparative tells you nothing reliable. Disambiguate in the clarify batch before
  drawing the option set — the alternative is a whole sheet set on the wrong room.
- **Openings are not absolute rects in a compiled model dump.** They are stored
  relative to the wall segment they sit in (`align: start|center|end` +
  `offset_mm`/width). Resolve them yourself (start = the segment's low-coordinate
  end, center = (span − width)/2) or read them off the sheet; do not conclude the
  doors are missing.
- **Vision reads of drawings are hypotheses.** Cross-check every number against a
  vector measurement (mm/pt factor) before it enters a drawing. Vision can also
  invent a plausible legible label where the glyphs are unreadable, and can read a
  rotated or mirrored crop backwards.
- **Label text size is fixed in sheet millimetres**, never derived from the world
  scale — a world-derived size collapses to unreadable at 1:56. One short line per
  zone, centred on free floor, not on furniture.
- **Doors in crowded option panels: draw the leaf only, no swing arc.** The arc
  quadrant collides with beds and cabinets and the defect reads as a real clash.
  Keep cabinets and wardrobes clear of the 900 mm swing quadrant at each door.
- **Review images: keep ≤ ~1500 px on the long edge and split multi-panel sheets in
  half.** A 2400 px crop can stall the read; downscale to JPEG and retry once rather
  than abandoning the check.
- **A partition drawn to the interior face reads as "not connected to the wall"** in
  a vision review — that is a false positive. Check the coordinates before changing
  a correct drawing.
- **Do not hand-edit generated sheets.** Keep the generator in `reports/<...>/` and
  re-run it; hand edits are lost on the next regeneration.

## Support files

- `references/reading-measured-plans.md` — getting printed dimensions and wall
  positions out of a CAD-style architectural PDF, including mm/pt calibration.
- `references/option-sheet-production.md` — the A3 SVG option-sheet recipe:
  panel transform, draw order, dimensions, rasterising without a browser, and the
  vision self-review loop.
- `templates/panel_plan_sheet.py` — copy-and-edit generator: sheet/panel transform,
  walls, openings, furniture, labels, A3 sheet with N panels.
