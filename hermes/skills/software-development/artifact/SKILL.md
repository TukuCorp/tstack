---
name: artifact
description: "Build a polished HTML page (report, explainer, dashboard, comparison, slides) the way a Claude artifact would be, review it with the user in Lavish, and share a private link only on request, using the lavish-axi CLI. Use when the user says /artifact, 'make an artifact', 'html publish artifact', or asks for a shareable or mobile-friendly page. For a quick review loop on a plan or diff without the house checks, use lavish."
version: 1.0.0
author: tukum (TukuCorp)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [html, artifacts, report, visualization]
---

# Artifact

Build a polished, self-contained HTML page (report, explainer, dashboard, comparison, slides), review it with the user in Lavish, and optionally give them a link. This is the house equivalent of a Claude artifact for agents without that tool. Claude artifacts give a private claude.ai link, versioning and pages that store data; here pages are local files, reviewed in Lavish and shared only on request.

`lavish-axi` is installed globally; if it is missing, use `npx -y lavish-axi` with the same arguments. Workflow and design guidance live in the CLI, not here: read them fresh each time.

## 1. Plan the page
- Name the reader and the one decision or understanding the page must give them. If the request is unclear on audience or language, ask once.
- Pick the playbooks: run `lavish-axi design`, then `lavish-axi playbook <id>` for every one that fits (diagram, table, comparison, plan, explanation, slides, input). A page often needs several.

## 2. Write it
- One HTML file at `.lavish/<YYYY-MM-DD>-<slug>.html` in the working directory, unless the user names a place. Copy local images next to it and use relative paths.
- Design source, in this order: a look the user named, the subject project's own design system, then the Lavish CDN default. Say which you used.
- House defaults:
  - Fewer words, more visuals: charts, diagrams, stat tiles, tables. Run the `unslop` skill on all prose before showing it.
  - Cite each factual claim to its original source in a footnote with URL and date. Never cite our own generated files or notes as evidence.
  - Vietnamese when asked: natural Vietnamese using the source's own terms, not a translation of the English. A language toggle must be visible at phone width.
  - Phone first: 16px side gutter, no horizontal scroll, controls reachable at 390px wide. Light and dark themes from CSS variables. Pin exact versions on any CDN script.

## 3. Check it
- Run `python -X utf8 C:/Users/<USER>/.claude/skills/verify/scripts/shot.py <file>` and look at the PNGs. Fix any overflow or off-screen control it flags.
- Compare the phone and desktop shots for buttons and toggles: a control visible on desktop but missing on the phone is a bug, even if the script does not flag it.
- Show the command and its result as proof.

## 4. Review in Lavish
- Open it with `lavish-axi <file>` and follow `lavish-axi --help` for the poll and reply loop. Keep the poll in the foreground.
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
