## Testing
- Test at the highest feasible level: **E2E** (nothing mocked; test accounts only) → **integration** (real DB/API/schema boundaries) → **golden** (real inputs, checked-in outputs; each edge-case bug adds a case) → **unit** (only for pure logic or math).
- Red/green: write the failing test first, at that level, and confirm it fails before implementing.
- No coverage-padding or mock-assertion tests. Project rules override these.
