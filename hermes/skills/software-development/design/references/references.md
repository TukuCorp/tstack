# References and the swipe file

References show which parts of an existing design to borrow: a density, a header pattern, a way of ordering information. They are never something to copy.

## Capturing a reference (`/design refs <urls|files>`)

For each URL:
1. `agent-browser` (headless; run `agent-browser skills get core` once per session): open the URL, then screenshot it at phone and desktop size into `.design/<slug>/refs/<host>-<n>-{phone,desktop}.png`. Run `agent-browser close` when done.
2. From the page, note the layout skeleton, the type scale, the spacing rhythm, 3-6 colour roles and one or two signature moves. Write these to `refs/<host>-<n>.md`.
3. Add one line to the contract saying what this reference contributes and what to leave behind.

For images or screenshots, copy them into `refs/` and write the same notes by looking at them. For the user's past artifacts or repo pages, link their path and take the notes the same way.

If a page needs the user's login, ask whether to use their logged-in browser. Don't sign in yourself.

Never put a reference's logo, product name, copy, photos or icons into an option. Rebuild the structure in the contract's tokens.

## Swipe file (`~/wiki/design/swipe/`)

The swipe file is a long-lived library of references and picked parts that the user marked "keep". It lives in the wiki, so every harness sees the same one.

Each entry has a thumbnail plus a note:
- `~/wiki/design/swipe/<yyyy-mm-dd>-<slug>.webp`, about 150 KB at most. Use `python -X utf8 -c` with PIL only for a one-line resize. For anything longer, write a script file.
- `~/wiki/design/swipe/<yyyy-mm-dd>-<slug>.md`, in this form:

```markdown
---
tags: [dense-table, dashboard, dark]
source: <url or "own: .design/<slug>/final">
date: 2026-11-25
---
Why kept: <the user's words; mark (inferred) if not theirs>
Moves: <1-3 structural moves worth reusing>
Avoid: <what not to take from it>
```

To search it at step 2, grep the `.md` notes for the brief's surface and tags: `python -X utf8 ~/wiki/scripts/recall.py "<tag|word>"` searches the whole wiki, or grep `~/wiki/design/swipe/*.md` directly. Use at most 3 swipe entries per run, and name each one in the contract.
