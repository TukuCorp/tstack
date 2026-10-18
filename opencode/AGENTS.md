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
- After any user correction: record the pattern and a rule that prevents recurrence. Project-specific → `lessons.md` at project root. Applies across projects → the Environment section below.
- Review `lessons.md` at session start for project-relevant rules.

## Environment (Windows 11)
- Git Bash (MSYS) rewrites arguments that start with `/` into Windows paths (`/codebase` → `C:/Program Files/Git/codebase`). Send them from PowerShell, or set `MSYS_NO_PATHCONV=1`, when the leading slash is literal (agent prompts, slash commands, URL paths, regexes).
- Python's `open()` defaults to cp1252 here: pass `encoding="utf-8"` when reading or writing text.

## Skill Routing
- Office files: `officecli` for inspecting, proofreading and surgical edits; `present` to fill a supplied template; `apdeck` for Allotrope-branded decks.
- Interviews: `brainstorm` for an open idea that should end in a research doc; `grilling` to stress-test an existing plan.

## Implementation Standards
- **Testing:**
  - Test at the highest feasible level: **E2E** (nothing mocked; test accounts only) → **integration** (real DB/API/schema boundaries) → **golden** (real inputs, checked-in outputs; each edge-case bug adds a case) → **unit** (only for pure logic or math).
  - Red/green: write the failing test first, at that level, and confirm it fails before implementing.
  - No coverage-padding or mock-assertion tests. Project rules override these.
- **When uncertain:** Use the most conventional approach, follow existing patterns, leave a single inline comment documenting the assumption.
- **Simplicity First:** Make every change as simple as possible. Impact minimal code.
- **No Laziness:** Find root causes. No temporary fixes. Senior developer standards.

## Verification Before Done
- Never mark a task complete without proving it works: run tests, check logs, demonstrate correctness.
- Ask yourself: "Would a staff engineer approve this?"
- Diff behavior between main and your changes when relevant.

## Elegance Check
- For non-trivial changes: pause and ask "is there a more elegant way?"
- If a fix feels hacky: implement the elegant solution instead.
- Skip this for simple, obvious fixes — don't over-engineer.

## Debugging Rules
- On test failure: analyze the error output and logs before changing code.
- If the same bug persists after two fix attempts: stop, summarize the current state and what was tried, and ask for direction.

## Core Behavior
- **Batch your work.** Complete the entire task in one response. Do not break work into steps that require approval.
