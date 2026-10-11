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

## Task Management
- Write a plan to `activeContext.md` at project root with checkable items before starting implementation.
- Check in with the user before beginning implementation when plan mode is active.
- Mark items complete as you go.
- Add a review/results section to `activeContext.md` after completion.
- After any user correction: update `lessons.md` at project root with the pattern and a rule that prevents recurrence.
- Review `lessons.md` at session start for project-relevant rules.

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
