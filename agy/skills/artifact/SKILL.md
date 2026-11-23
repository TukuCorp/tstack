---
name: artifact
description: "Build a polished HTML page (report, explainer, dashboard, comparison, slides) the way a Claude artifact would be, review it with the user in Lavish, and share a private link only on request, using the lavish-axi CLI. Use when the user says /artifact, 'make an artifact', 'html publish artifact', or asks for a shareable or mobile-friendly page. For a quick review loop on a plan or diff without the house checks, use lavish."
---

# Artifact

Build a polished, self-contained HTML page (report, explainer, dashboard, comparison, slides), review it with the user in Lavish, and optionally give them a link. This is the house equivalent of a Claude artifact for agents without that tool. Claude artifacts give a private claude.ai link, versioning and pages that store data; here pages are local files, reviewed in Lavish and shared only on request.

`lavish-axi` is installed globally; if it is missing, use `npx -y lavish-axi` with the same arguments. Workflow and design guidance live in the CLI, not here: read them fresh each time.

## 1. Plan the page
- Name the reader and the one decision or understanding the page must give them. If the request is unclear on audience or language, ask once.
- Pick the playbooks: run `lavish-axi design`, then `lavish-axi playbook <id>` for every one that fits (diagram, table, comparison, plan, explanation, slides, input). A page often needs several.

## 2. Write it
- One HTML file at `.lavish/<YYYY-MM-DD>-<slug>.html` in the working directory (local date from `date +%F`), unless the user names a place. Copy local images next to it and use relative paths.
- Create the file with a short Python script that writes UTF-8 (`open(path, "w", encoding="utf-8")`) or your file-write tool. Never push a whole page through `apply_patch`: HTML lines break its hunk parser.
- Design source, in this order: a look the user named, the subject project's own design system, then the Lavish CDN default. Say which you used.
- House theme, overriding Lavish's `data-theme="luxury"` default (dark only, gold): leave `<html>` without a dark `data-theme` so DaisyUI follows the system light/dark, or define CSS variables with a `prefers-color-scheme: dark` block. Accent teal `#0f7a6c` (dark `#3cc2ae`). Status colors ok `#2f855a`, warn `#b7791f`, bad `#c2410c` (dark `#6fcf97`, `#e6b75a`, `#f08a5d`), used the same way on chips, key numbers and chart marks. Every stat-tile number and verdict (OK, Gap, Risk) gets its status color as a colored chip, not plain text; a neutral white number on a judged item is a miss.
- House defaults:
  - Fewer words, more visuals: charts, diagrams, stat tiles, tables. Run the `unslop` skill on all prose before showing it.
  - Keep source wording exact: Vietnamese diacritics, names, table and page labels (`Bảng 55`, never `Bang 55`). Never transliterate to ASCII.
  - Cite each factual claim to its original source in a footnote, as a clickable `<a href>` link with the date. Never cite our own generated files or notes as evidence.
  - Vietnamese when asked: natural Vietnamese using the source's own terms, not a translation of the English. A language toggle must be visible at phone width.
  - Phone first: 16px side gutter, no horizontal scroll, controls reachable at 390px wide. Light and dark themes from CSS variables. Pin exact versions on any CDN script.

## 3. Check it
- Run `python -X utf8 <this skill's folder>/scripts/fidelity.py <source> <file>`, where `<source>` is the brief, notes or original the page was built from. Fix every FAIL (dropped diacritics, unlinked sources, dark-only theme). For each WARN number, confirm it was shown in a chart or dropped on purpose.
- Run `python -X utf8 C:/Users/<USER>/.claude/skills/verify/scripts/shot.py <file>` and look at the PNGs. Fix any overflow or off-screen control it flags.
- Compare the phone and desktop shots for buttons and toggles: a control visible on desktop but missing on the phone is a bug, even if the script does not flag it.
- Cap the check-and-fix loop at 3 rounds. If anything still fails, stop and hand over with the open issues listed rather than polishing further.
- Show the command and its result as proof.

## Interactive pages (maps, filters, dashboards, tools)
- Layout: `index.html` in its own folder under `.lavish/<date>-<slug>/`, code in `app.js` (split by job past ~800 lines: data, map, panels, i18n), data in `data/*.json` loaded with `fetch` and relative paths. Never paste large data into the HTML.
- Pin library versions (`d3@7.9.0`). For maps, project the real geometry (GeoJSON or TopoJSON) with d3-geo. Never draw a hand-made outline.
- One state object drives everything: filters, search, selection and language update the map, panels and counts together. Show an empty state when filters match nothing.
- Touch first: tap targets at least 40px, pinch and button zoom, the detail view as a bottom sheet. On phones the map or main visual must show on the first screen: filters go behind a "Filters" button (drawer), never stacked above the map.
- Check the interactions headlessly, not just the first screen. Run `lavish-axi stop` first if needed, serve the folder (`python -m http.server 8765`), then with `agent-browser`: `open` the page, `set viewport 393 852`, click one filter, one map feature and the language toggle, `screenshot` after each, and read `errors` and `console`. Any page error is a FAIL.
- Spot-check three totals shown in the UI (for example MW for one filter) against the data with a one-off script. For `fidelity.py`, the source is the data's text fields, not the page prose. Skip the word-count warning.
- A client-confidential dataset never goes to `share`; hand over the `export` file or the folder instead.

## 4. Review in Lavish
- Always finish by opening the page: `lavish-axi <file>` opens it in the user's default browser. Never pass `--no-open`. Status `opened` means a tab opened. Status `ready` means the browser did not launch, so give the user the printed `url`.
- If it fails with "server did not start", run `lavish-axi stop` and open it again. A stale server can hold port 4387.
- Then follow `lavish-axi --help` for the poll and reply loop. Keep the poll in the foreground.
- Apply the feedback to the same file. On an update, rewrite and merge sections; remove anything the new information makes outdated instead of appending.

## 5. Share (only when asked)
- Default to no link: the local file and Lavish session are the deliverable. `lavish-axi export <file>` gives a single portable HTML file for email or Drive.
- A link goes to ht-ml.app, a third-party host with no delete. Ask before sharing anything personal, family-health, financial or client-confidential, and suggest the exported file instead.
- When a link is wanted: `lavish-axi share <file> --private`. Give the user the URL and password, and say anyone with both can open it. Never share publicly unless the user says "public".
- Save the returned `site_id` and `update_key` to `<file>.share.json` next to the page (local only; never paste the key into chat or a commit). Later updates republish to the same URL: `lavish-axi share <file> --site <id> --update-key <key>`. `--unpublish` only hides the page; say so rather than calling it deleted.
- If the user needs a durable private link they can open from their phone, or a page that stores data (tracker, sign-up sheet), say in one line that Claude Code can publish the same file as a claude.ai artifact.

## Request

$ARGUMENTS

If the request above is empty, build the page from what the conversation asked for.
