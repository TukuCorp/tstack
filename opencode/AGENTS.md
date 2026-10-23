# Guidelines

## Initialization
- Read `AGENTS.md` if available at the start of every session to understand project laws (tech stack, testing framework, standards).

## Research Before Code
- Read relevant files, docs, and config before generating code.
- For large codebases, identify only the files relevant to the current task — do not fill the context window with irrelevant files.

## Subagent Strategy
- Use subagents to keep the main context window clean.
- Offload research, exploration, and parallel analysis to subagents.
- One focused task per subagent for clarity.
- For complex problems, use more subagents rather than expanding context.
- Subagents start cold and cost tokens: do small lookups inline.

## Task Management
- For multi-step implementation work, write a plan to `activeContext.md` at project root with checkable items before starting. Skip it for questions and one-step changes.
- Give each task its own dated `##` section in `activeContext.md`; don't rewrite earlier tasks' sections.
- Check in with the user before beginning implementation when plan mode is active.
- Mark items complete as you go.
- Add a review/results section to `activeContext.md` after completion.
- After any user correction: record the pattern and a rule that prevents recurrence. Project-specific → `lessons.md` at project root. Applies across projects → this global file (and the other harnesses' global rule files).
- Review `lessons.md` at session start for project-relevant rules.

## Implementation Standards
- **Testing:**
  - Test at the highest feasible level: **E2E** (nothing mocked; test accounts only) → **integration** (real DB/API/schema boundaries) → **golden** (real inputs, checked-in outputs; each edge-case bug adds a case) → **unit** (only for pure logic or math).
  - Red/green: write the failing test first, at that level, and confirm it fails before implementing.
  - No coverage-padding or mock-assertion tests. Project rules override these.
- **When uncertain:** Use the most conventional approach, follow existing patterns, leave a single inline comment documenting the assumption.
- **Simplicity First:** Make every change as simple as possible. Impact minimal code.
- **No Laziness:** Find root causes. No temporary fixes. Senior developer standards.

## Debugging Rules
- On test failure: analyze the error output and logs before changing code.
- If the same bug persists after two fix attempts: stop, summarize the current state and what was tried, and ask for direction.

## Core Behavior
- **Batch your work.** Complete the entire task in one response. Do not break work into steps that require approval.

## Browser Use
- chrome-devtools-axi attaches to my own everyday Chrome (`CHROME_DEVTOOLS_AXI_AUTO_CONNECT=1`), which I am using at the same time. Never disturb my tabs:
  - Open every page with `chrome-devtools-axi newpage <url> --background`. Never use `open` or `selectpage` on a tab you didn't create, and never navigate, click, type or close in my tabs.
  - Work only in tabs you opened; close them with `closepage` when done.
  - For Google files, add `authuser=<EMAIL>` (the work account is not the default).

## Personal Wiki
- `~/wiki` (private) holds durable context about me, my projects and past decisions, gathered from every agent. When a task needs that background, read `~/wiki/index.md`, then the pages it points to.
- Save durable facts to your own memory store if you have one (a daily sync folds it into the wiki); otherwise write them into the wiki following `~/wiki/AGENTS.md` (Ingest).
