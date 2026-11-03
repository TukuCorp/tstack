## Testing
- Test at the highest feasible level: **E2E** (nothing mocked; test accounts only) → **integration** (real DB/API/schema boundaries) → **golden** (real inputs, checked-in outputs; each edge-case bug adds a case) → **unit** (only for pure logic or math).
- Red/green: write the failing test first, at that level, and confirm it fails before implementing.
- No coverage-padding or mock-assertion tests. Project rules override these.

## Google Workspace
- For Gmail, Drive, Docs, Sheets, Slides and Calendar, use the `gws` CLI first (`gws <service> --help`), before connectors/MCP, browser or desktop automation. When another route fails on a Google task, switch to `gws` instead of retrying it.
- Bare `gws` is the work account (<EMAIL>). Test access with a real API call before any login flow: `gws auth login` replaces the whole scope grant, so a narrower re-login breaks other jobs.
- Syntax, accounts and Windows quirks: `~/wiki/wiki/gws-cli.md`.

## Browser Use
- Logged-in Chrome (my real profile, which I am using at the same time): use `browser-control`, and load the browser-control skill first. Work only in sessions and tabs you created; never navigate, click, type or close in my tabs. Leave the `gdrive-daily` session alone: a scheduled job uses it.
- Headless or throwaway browsing (public pages, localhost testing, scraping, screenshots): use `agent-browser`. Run `agent-browser skills get core` before the first use in a session, and `agent-browser close` when done.
- For Google files, add `authuser=<EMAIL>` (the work account is not the default).

## Desktop Apps
- Use `agent-desktop` to see and operate native desktop apps through the OS accessibility tree. Before the first use in a session, run `agent-desktop skills get desktop` and `agent-desktop skills get platform`, and follow them.
- Stay headless (the default): never pass `--headed` unless I allow physical input for that task, because it moves my cursor and takes focus while I am using the machine.
- For live PowerPoint or Excel, prefer xlwings or officecli, then the PowerPoint MCP (see MCP Servers); use agent-desktop for apps without an API.
- UWP apps hosted by ApplicationFrameHost (Calculator) expose only their title bar; report that instead of retrying.
- In PowerShell, quote every ref (`'@s8f3k2p9:e1'`).

## MCP Servers
- Prefer a tool's CLI over its MCP server; use the MCP only when the CLI can't do the task.
- officecli: `officecli`. NotebookLM: `nlm` (`nlm --ai` prints agent docs). Firecrawl: `firecrawl` (`firecrawl --help`; search, scrape, crawl, map). Live PowerPoint has no CLI: use xlwings or officecli on the file, else the PowerPoint MCP.

## Personal Wiki
- `~/wiki` (private) holds durable context about me, my projects and past decisions, gathered from every agent. When a task needs that background, read `~/wiki/index.md`, then the pages it points to.
- Save durable facts to your own memory store if you have one (a daily sync folds it into the wiki); otherwise write them into the wiki following `~/wiki/AGENTS.md` (Ingest).

## Allotrope Decks
- "Allotrope format" means the real house template, not the apdeck navy/Calibri spec: copy `~/Downloads/ee-heat/gap/Call Notes & Meetings/2026_Allotrope-Gap Kickoff Call v7 final.pptx` (Cabin, teal banner, solar/wind cover), keep its cover, clone its banner, draw native shapes. Pattern: `ee-heat/reports/build_gap_priorities_on_template.py`.
