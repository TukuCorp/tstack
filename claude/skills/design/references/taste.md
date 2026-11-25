# Taste: learning from picks

Taste rules turn what the user chose, grafted, rejected or silently edited into reusable rules, so later runs start closer to what they like.

## Where it lives

- **Global:** `~/wiki/wiki/design/taste.md` is shared by every harness. Create it on first write with the heading `# Design taste` and one `##` section per class: Layout, Type, Colour, Density, Motion, Copy, Components.
- **Project:** `DESIGN.md` in the project root holds tokens, personality and patterns to reject. Where it conflicts with the global file, the project file wins. Propose creating it when a project has had 2 or more runs and no `DESIGN.md`.

## What counts as a signal

In order of strength:
1. **Silent edits:** the user changed a kept option by hand.
2. **Grafts:** what was carried over, and from where.
3. **Explicit notes and rejections** in the picker.
4. **The base pick** on its own. This is the weakest signal, because it says "better than the others", not "good".

## Writing a rule

Generalise to the class, not the instance. "Prefer tables over cards when rows have 4 or more comparable fields" is a rule. "Use a table on the invoices page" is an instance. Format:

```markdown
- Prefer <x> over <y> when <condition>. Why: <user's words> (2026-11-25, .design/<slug>)
- Prefer <x> over <y> when <condition>. Why (inferred): <your reading> (2026-11-25, .design/<slug>)
```

Propose 0-3 rules per `keep`, then stop and wait for the user's OK. Zero is a fine answer when the picks don't generalise. Before adding a rule, check whether it contradicts an existing one. If it does, show both and ask which one stands.

When a rule can be checked mechanically (a colour that is banned, a minimum tap size), propose adding it to the `SLOP` list in `gates.py` as well. A lint check holds better than a sentence.

After writing, log one line: `python -X utf8 ~/wiki/scripts/note.py --tool <harness> "design: kept <slug>, +<n> taste rules"`.
