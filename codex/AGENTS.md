## Testing
- Test at the highest feasible level: **E2E** (nothing mocked; test accounts only) → **integration** (real DB/API/schema boundaries) → **golden** (real inputs, checked-in outputs; each edge-case bug adds a case) → **unit** (only for pure logic or math).
- Red/green: write the failing test first, at that level, and confirm it fails before implementing.
- No coverage-padding or mock-assertion tests. Project rules override these.

## Browser Use
- chrome-devtools-axi attaches to my own everyday Chrome (`CHROME_DEVTOOLS_AXI_AUTO_CONNECT=1`), which I am using at the same time. Never disturb my tabs:
  - Open every page with `chrome-devtools-axi newpage <url> --background`. Never use `open` or `selectpage` on a tab you didn't create, and never navigate, click, type or close in my tabs.
  - Work only in tabs you opened; close them with `closepage` when done.
  - For Google files, add `authuser=<EMAIL>` (the work account is not the default).
