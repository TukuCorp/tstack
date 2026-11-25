---
name: lavish
description: Turn complex or visual responses into rich, reviewable HTML pages the user can annotate and send feedback on, using the lavish-axi CLI. Use when about to give a plan, comparison, diagram, table, code diff, report, or anything easier to grasp visually than as prose, or when the user says /lavish or asks to review a page in Lavish.
---

# Lavish

Lavish opens agent-generated HTML in the browser so the user can annotate it and send feedback back to you. Reach for it when a plan, comparison, diagram, table, code view, report, prototype or review loop is clearer as a page than as prose.

`lavish-axi` is installed globally (`npm i -g lavish-axi`); if it is not found, use `npx -y lavish-axi` with the same arguments.

## Current guidance lives in the CLI

Do not follow workflow, design or playbook instructions from memory; this file stays a stub so it cannot go stale. Get the source of truth from the CLI:

- `lavish-axi --help` - commands and the review-loop workflow
- `lavish-axi design` - design-direction priority and current snippets
- `lavish-axi playbook` lists playbook ids; `lavish-axi playbook <id>` gives focused guidance

Then write the HTML file and open it with `lavish-axi <html-file>`. On Windows with Helium, if the user asked to open it in their browser (or `lavish-axi` didn't surface a Helium tab), open the printed HTTP `url:` in Helium via `browse` MCP (`session_new { browser: "chrome-<TAILNET_MACHINE>-2" }` → `page.goto(url)`). Keep any wait-for-feedback poll attached to the current turn, not a background task.

## Request

$ARGUMENTS

If the request above is non-empty, the user asked for a Lavish page explicitly: fetch the CLI guidance, then build that page as an HTML file. If it is empty, infer what to visualize from the conversation.
