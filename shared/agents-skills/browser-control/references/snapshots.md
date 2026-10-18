# Snapshots And Labeled Screenshots

## Accessibility Snapshot

Prefer `snapshot()` for the compact read-before-act happy path. It uses the
page's single `main` region when available, collapses navigation, and spends its
bounded item budget on alerts, semantic groups, lists, tables, block code,
headings, primary links, and controls before repeated metadata. It summarizes
select option counts, pairs table headers with row cell values, and assigns refs
to controls. Its timeout defaults to 10 seconds to accommodate a cold first
browser evaluation. Text input and textarea values are omitted:

```js
return await snapshot()
```

Use a returned ref on the next execute call as a Playwright locator:

```js
await ref("e12").click()
```

Refs belong to the latest snapshot and are rejected after main-frame navigation.
They combine structural position with captured accessible identity, so sibling
DOM drift fails closed instead of silently retargeting a different named control.
Drill into omitted context with `snapshot({ within, interactive, compact, depth,
maxItems, timeout })`.

After a full snapshot establishes a baseline, use `snapshot({ diff: true })`
with the same page and shape options to return only semantic additions and
removals plus an unchanged count:

```js
await ref("e12").click()
return await snapshot({ diff: true })
```

Each successful diff becomes the next baseline. A diff invalidates earlier refs
and assigns current refs only to added or changed lines. Take another full
snapshot before acting on an unchanged element.

Use `ariaSnapshot(target?, { timeout })` when the compact view omitted needed
structure. It defaults to a 5-second timeout and
returns Playwright's YAML aria snapshot for a selector, locator, or the whole
page (default `body`), so one call shows you whether a "tab bar" is really a
`<select>`, what a control's accessible name is, and which roles exist —
without burning a 30s locator timeout on a wrong `getByRole` guess:

```js
return await ariaSnapshot("main", { timeout: 10_000 })
```

Omit the options for the 5-second default, or override `timeout` in milliseconds
for a deliberately slow region. Use `screenshotWithLabels` when you need visual
layout rather than structure, and raw Playwright when neither snapshot shape is
specific enough.

## Labeled Screenshots

Use `screenshotWithLabels({ page, path? })` when a visual page read would help.
The helper overlays simple `e1`, `e2`, ... labels on visible likely-interactive
elements, captures a Playwright screenshot, removes the overlay, and returns
image plus label metadata. Omit `path` and return the result through MCP for an
in-memory attachment; when supplied, `path` must be absolute and the image is
saved instead.

```js
// Absolute path written literally: the relay's working directory is not your shell's.
const screenshotPath = "C:/Users/tukum/project/tmp/home-labels.png"
return await screenshotWithLabels({ page, path: screenshotPath })
```

Labels cover a small DOM-only set: buttons, links, inputs, textareas, selects,
`role=button/link/tab/menuitem`, `[onclick]`, and `[contenteditable]`. Each
label entry carries its `ref` (`e1`, `e2`, ...), a `selector` for the next
Playwright locator, and, when ambiguous, a short `context` string from the
nearest row/section/heading so identical buttons (five "Connect" buttons in
five integration rows) are distinguishable without another round-trip.
