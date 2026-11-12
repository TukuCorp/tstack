# Guidelines

## Initialization
- Read `AGENTS.md` if available at the start of every session to understand project laws (tech stack, testing framework, standards).

## Subagents
- Delegate only substantial standalone work (audits, migrations, bulk or verbose reading), one focused task each. Do small jobs inline: subagents add cost and latency and don't make the answer smarter.
- Put delegated searching and reading on a cheaper model; keep code edits on the main model.

## Task Management
- For multi-step implementation work, write a plan to `activeContext.md` at project root with checkable items before starting. Skip it for questions and one-step changes.
- Give each task its own dated `##` section in `activeContext.md`; don't rewrite earlier tasks' sections.
- Check in with the user before beginning implementation when plan mode is active.
- Mark items complete as you go.
- Add a review/results section to `activeContext.md` after completion.
- When I correct the same thing twice: record the pattern and a rule that prevents recurrence, as a hook or lint rule if it must never bend. Project-specific → `lessons.md` at project root. Applies across projects → this global file (and the other harnesses' global rule files).
- Review `lessons.md` at session start for project-relevant rules.

## Implementation Standards
- **Testing:**
  - Test at the highest feasible level: **E2E** (nothing mocked; test accounts only) → **integration** (real DB/API/schema boundaries) → **golden** (real inputs, checked-in outputs; each edge-case bug adds a case) → **unit** (only for pure logic or math).
  - Red/green: write the failing test first, at that level, and confirm it fails before implementing.
  - No coverage-padding or mock-assertion tests. Project rules override these.
- **When uncertain:** Use the most conventional approach, follow existing patterns, leave a single inline comment documenting the assumption.
- **File size:** Keep each code file at 1000 lines or fewer. In a new repo, add a lint rule for it before much code exists (ESLint `max-lines`, pylint `max-module-lines`, or a test that counts lines); unwinding big files later is costly. Split a file that nears the cap by responsibility.
- **Simplicity First:** Make every change as simple as possible. Impact minimal code.
- **Root causes:** Fix the cause, not the symptom; no temporary fixes.

## Shell on Windows
- Write any script longer than a few lines to a scratch file (Write tool) and run the file. Long programs inlined in `bash -c`, heredocs or PowerShell strings break on quotes.
- Give native Windows programs (python, gws, PIL) `C:/...` paths, not Git Bash `/c/...` paths.
- Run Python as `python -X utf8`, or Unicode output crashes on cp1252. Add `-I` only for scripts that read untrusted downloads: it ignores `PYTHONUTF8` and drops the script's own folder from imports (`No module named ...`).

## Verification
- End each task with a runnable check (test, build, script, screenshot) and show the command and its output as proof; "looks done" is not done.
- When a result falls short, escalate in order: add or tighten that check, then raise effort one level, then move up a model.
- Briefs (my prompts, subagent and swarm lanes, scheduled jobs) state Goal, Why, Constraints, Out of scope and Check. Leave out what the agent can read from the repo.
- Unattended runs (loops, swarms, scheduled jobs) also set a turn or spend limit and say where output lands for my approval. Pilot on about 3 items before running the rest.
- Review in a fresh context for correctness, not style. Cap review at 3 rounds, then review only the new diff. A finding that keeps recurring goes into a lint rule, the repo's `REVIEW.md`, or the skill that caused it.

## Debugging Rules
- If the same bug persists after two fix attempts: stop, summarize the current state and what was tried, and ask for direction. The next attempt starts from a fresh session with a rewritten prompt, not more patches.

## Core Behavior
- **Batch your work.** Complete the entire task in one response. Do not break work into steps that require approval.

## Google Workspace
- For Gmail, Drive, Docs, Sheets, Slides and Calendar, use the `gws` CLI first (`gws <service> --help`), before connectors/MCP, browser or desktop automation. When another route fails on a Google task, switch to `gws` instead of retrying it.
- Bare `gws` is the work account (<EMAIL>). Test access with a real API call before any login flow: `gws auth login` replaces the whole scope grant, so a narrower re-login breaks other jobs.
- Syntax, accounts and Windows quirks: `~/wiki/wiki/gws-cli.md`.

## Browser Use
- Logged-in Chrome (my real profile, which I am using at the same time): use `browse` (MCP server or CLI), and load the browse skill first. Work only in sessions and tabs you created or that I lent you with the toolbar button; never navigate, click, type or close in my other tabs. Leave the `gdrive-daily` session alone: a scheduled job uses it.
- Headless or throwaway browsing (public pages, localhost testing, scraping, screenshots): use `agent-browser`. Run `agent-browser skills get core` before the first use in a session, and `agent-browser close` when done.
- For Google files, add `authuser=<EMAIL>` (the work account is not the default).

## Desktop Apps
- Use `agent-desktop` to see and operate native desktop apps through the OS accessibility tree. Before the first use in a session, run `agent-desktop skills get desktop` and `agent-desktop skills get platform`, and follow them.
- Stay headless (the default): never pass `--headed` unless I allow physical input for that task, because it moves my cursor and takes focus while I am using the machine.
- Headless still is not focus-safe on Windows: UI Automation focus calls can raise the target window and take keyboard focus (Cua Driver Bench, 2026-11). While I am using the machine, prefer an API route (xlwings, officecli, gws) and tell me before driving another app.
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
