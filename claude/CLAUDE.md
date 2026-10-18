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
- After any user correction: record the pattern and a rule that prevents recurrence. Project-specific → `lessons.md` at project root. Applies across projects → the Environment section below (and the other harnesses' global rule files).
- Review `lessons.md` at session start for project-relevant rules.

## Environment (Windows 11)
- Git Bash (MSYS) rewrites arguments that start with `/` into Windows paths (`/codebase` → `C:/Program Files/Git/codebase`). Send them from PowerShell, or set `MSYS_NO_PATHCONV=1`, when the leading slash is literal (agent prompts, slash commands, URL paths, regexes).
- Python's `open()` defaults to cp1252 here: pass `encoding="utf-8"` when reading or writing text.

## Tool Routing
- Browser: `chrome-devtools-axi` for general browsing, screenshots and DevTools; `browser-control` only for scripted Playwright against logged-in tabs or when named; claude-in-chrome when asked.
- Office files: `officecli` for inspecting, proofreading and surgical edits; `present` to fill a supplied template; `apdeck` for Allotrope-branded decks; pptx/docx/xlsx skills when there's no template.
- Research: the `research` skill for cited briefs; the `ask` agent for quick single-question lookups and git archaeology.
- Interviews: `brainstorm` for an open idea that should end in a research doc; `grilling` to stress-test an existing plan.

## Deliverable File Placement
- **Every deliverable goes in the project folder**, never in the scratchpad, `~/Downloads`, or a system temp directory. This applies to reports, spreadsheets, PDFs, decks, diagrams, screenshots kept as evidence — anything the user will open, keep, or send on.
- Put it in an existing folder that fits, or create a clearly named one at project root (e.g. `training-costs/`, `flight-prices/`).
- **If it must not be committed, add it to `.gitignore` — do not move it out of the project.** A project law saying material "may never be committed" is satisfied by gitignoring it, not by exiling it to a temp folder.
- The scratchpad is only for throwaway intermediates: build scripts, cropped images, raw tool dumps. If the user would ever want the file again, it does not belong there.
- Tell the user the project-relative path when you hand a deliverable over.

## Verification Before Done
- Never mark a task complete without proving it works: run tests, check logs, demonstrate correctness.
- Ask yourself: "Would a staff engineer approve this?"
- Diff behavior between main and your changes when relevant.

## Elegance Check
- For non-trivial changes: pause and ask "is there a more elegant way?"
- If a fix feels hacky: implement the elegant solution instead.
- Skip this for simple, obvious fixes — don't over-engineer.
