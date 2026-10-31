## Testing
- Test at the highest feasible level: **E2E** (nothing mocked; test accounts only) → **integration** (real DB/API/schema boundaries) → **golden** (real inputs, checked-in outputs; each edge-case bug adds a case) → **unit** (only for pure logic or math).
- Red/green: write the failing test first, at that level, and confirm it fails before implementing.
- No coverage-padding or mock-assertion tests. Project rules override these.

## Desktop Apps
- Use `agent-desktop` to see and operate native desktop apps through the OS accessibility tree. Before the first use in a session, run `agent-desktop skills get desktop` and `agent-desktop skills get platform`, and follow them.
- Stay headless (the default): never pass `--headed` unless I allow physical input for that task, because it moves my cursor and takes focus while I am using the machine.
- For live PowerPoint or Excel, prefer the PowerPoint MCP, xlwings or officecli; use agent-desktop for apps without an API.
- UWP apps hosted by ApplicationFrameHost (Calculator) expose only their title bar; report that instead of retrying.
- In PowerShell, quote every ref (`'@s8f3k2p9:e1'`).

## Personal Wiki
- `~/wiki` (private) holds durable context about me, my projects and past decisions, gathered from every agent. When a task needs that background, read `~/wiki/index.md`, then the pages it points to.
- Save durable facts to your own memory store if you have one (a daily sync folds it into the wiki); otherwise write them into the wiki following `~/wiki/AGENTS.md` (Ingest).
