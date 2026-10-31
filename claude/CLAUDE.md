# Guidelines

## Initialization
- Treat the project `CLAUDE.md` as project law (tech stack, testing framework, standards).
- In a code repo with no project `CLAUDE.md`, ask about the tech stack, testing framework, and coding standards before writing code. Outside code repos (home folder, admin or expense work), don't ask.

## Research Before Code
- Read relevant files, docs, and config before generating code.
- For large codebases, identify only the files relevant to the current task — do not load the entire project.

## Implementation Standards
- **Testing:**
  - Test at the highest feasible level: **E2E** (nothing mocked; test accounts only) → **integration** (real DB/API/schema boundaries) → **golden** (real inputs, checked-in outputs; each edge-case bug adds a case) → **unit** (only for pure logic or math).
  - Red/green: write the failing test first, at that level, and confirm it fails before implementing.
  - No coverage-padding or mock-assertion tests. Project rules override these.
- **When uncertain:** Use the most conventional approach, follow existing patterns, leave a single inline comment documenting the assumption.

## Debugging Rules
- On test failure: analyze the error output and logs before changing code.
- If the same bug persists after two fix attempts: stop, summarize the current state and what was tried, and ask for direction.

## Core Principles
- **Simplicity First:** Make every change as simple as possible. Impact minimal code.
- **No Laziness:** Find root causes. No temporary fixes. Senior developer standards.

## Subagent Strategy
- Use subagents to keep the main context window clean.
- Offload research, exploration, and parallel analysis to subagents.
- One focused task per subagent for clarity.
- For complex problems, use more subagents rather than expanding context.
- Subagents start cold and cost tokens: do small lookups inline.

## Task Management
- For multi-step implementation work, write a plan to `activeContext.md` at project root with checkable items before starting. Skip it for questions and one-step changes.
- Give each task its own dated `##` section in `activeContext.md`; don't rewrite earlier tasks' sections.
- Check in with the user before beginning implementation, unless they already said to proceed or the task runs unattended (loops, scheduled jobs).
- Mark items complete as you go.
- Add a review/results section to `activeContext.md` after completion.
- After any user correction: record the pattern and a rule that prevents recurrence. Project-specific → `lessons.md` at project root. Applies across projects → this global file (and the other harnesses' global rule files).
- Review `lessons.md` at session start for project-relevant rules.

## Browser Use
- Use Claude in Chrome (`mcp__claude-in-chrome__*`) first for any browser task. It works in its own tab group and does not trigger Chrome's remote-debugging prompt. Fall back to other browser tools only when it can't do the job (e.g. DevTools-level inspection, performance traces) or it fails after 2-3 attempts, and say why.
- chrome-devtools-axi attaches to my own everyday Chrome (`CHROME_DEVTOOLS_AXI_AUTO_CONNECT=1`), which I am using at the same time. Never disturb my tabs:
  - Open every page with `chrome-devtools-axi newpage <url> --background`. Never use `open` or `selectpage` on a tab you didn't create, and never navigate, click, type or close in my tabs.
  - Work only in tabs you opened; close them with `closepage` when done.
  - For Google files, add `authuser=<EMAIL>` (the work account is not the default).

## Desktop Apps
- Use `agent-desktop` to see and operate native desktop apps through the OS accessibility tree. Before the first use in a session, run `agent-desktop skills get desktop` and `agent-desktop skills get platform`, and follow them.
- Stay headless (the default): never pass `--headed` unless I allow physical input for that task, because it moves my cursor and takes focus while I am using the machine.
- For live PowerPoint or Excel, prefer the PowerPoint MCP, xlwings or officecli; use agent-desktop for apps without an API.
- UWP apps hosted by ApplicationFrameHost (Calculator) expose only their title bar; report that instead of retrying.
- In PowerShell, quote every ref (`'@s8f3k2p9:e1'`).

## Personal Wiki
- `~/wiki` (private) holds durable context about me, my projects and past decisions, gathered from every agent. When a task needs that background, read `~/wiki/index.md`, then the pages it points to.
- Save durable facts to your own memory store if you have one (a daily sync folds it into the wiki); otherwise write them into the wiki following `~/wiki/AGENTS.md` (Ingest).
