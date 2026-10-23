## Testing
- Test at the highest feasible level: **E2E** (nothing mocked; test accounts only) → **integration** (real DB/API/schema boundaries) → **golden** (real inputs, checked-in outputs; each edge-case bug adds a case) → **unit** (only for pure logic or math).
- Red/green: write the failing test first, at that level, and confirm it fails before implementing.
- No coverage-padding or mock-assertion tests. Project rules override these.

## Personal Wiki
- `~/wiki` (private) holds durable context about me, my projects and past decisions, gathered from every agent. When a task needs that background, read `~/wiki/index.md`, then the pages it points to.
- Save durable facts to your own memory store if you have one (a daily sync folds it into the wiki); otherwise write them into the wiki following `~/wiki/AGENTS.md` (Ingest).
