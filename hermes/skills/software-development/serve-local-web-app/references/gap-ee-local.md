# gap-ee local serving — static HTML via http.server + browser-control

Source session: 2026-08-28 — <PRIVATE_REPO>/teach-workspace/gap-ee.

## Why http.server (not file://)

gap-ee lessons load `../assets/style.css` + `../assets/quiz.js` with relative
paths. `file://` breaks those in some contexts and differs from the verifier's
expectation. Serving the workspace root via `http.server` mirrors how a real
deploy would serve them and keeps asset resolution stable.

## Server command

```bash
python -m http.server 8011 --directory "C:/Users/tukum/Downloads/<PRIVATE_REPO>/teach-workspace"
# background (Hermes): terminal(background=true, notify_on_complete=true)
# verify:
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8011/gap-ee/lessons/0001-thermo-and-heat-transfer-primer.html  # 200
curl -s http://127.0.0.1:8011/gap-ee/lessons/ | grep href
```

If port 8011 is taken: `netstat -ano | grep 8011`, `wmic process where "ProcessId=<pid>" get CommandLine,CreationDate` — kill stale with `taskkill /PID <pid> /F` (single slash, not //).

## Gap-EE scope

Week 1 (0001-0005) — what "first week" means when the user says it:

- 0001-thermo-and-heat-transfer-primer.html — week 1, day 1 (45-60m)
- 0002-refrigeration-cycle-and-cop.html — week 1, days 1-2 (45-60m)
- 0003-steam-systems-fundamentals.html — week 1, days 2-3 (45-60m)
- 0004-measur-hands-on-steam-and-waste-heat.html — week 1, days 3-4 (90-120m hands-on GUI)
- 0005-tea-lcoh-fundamentals.html — week 1, day 5 (45-60m)

Week 2 (do NOT open when only week 1 asked):

- 0006-reopt-hands-on-scenario-building.html — week 2, days 6-7
- 0007-tou-tariffs-and-breakeven-cop.html — week 2, day 7
- 0008-heat-pump-model-cross-check.html — week 2, day 8
- 0009-energyplus-envelope-hvac-orientation.html — week 2, day 9
- 0010-ihda-fied-methodology.html — week 2, days 9-10
- 0011-capstone-thermal-storage-sizing.html — week 2, days 11-14

Artifacts (self-contained HTML, primer set): `gap-ee/artifacts/0001` through `0003`
mirror lessons 0001-0003 (quiz, Carnot explorer, steam checklist).

Local file paths mirror URLs:
`C:/Users/tukum/Downloads/<PRIVATE_REPO>/teach-workspace/gap-ee/lessons/0001-*.html` etc.

## Browser-control multi-tab recipe (localhost)

Cloud `browser_exec` blocks localhost:

> Blocked: URL targets a private or internal address

Use the local relay (user's Chrome, 127.0.0.1:19989) — it reaches localhost:

```bash
browser-control session new gap-ee-week1
browser-control execute --session gap-ee-week1 'await page.goto("http://127.0.0.1:8011/gap-ee/lessons/0001-thermo-and-heat-transfer-primer.html", {waitUntil:"domcontentloaded"}); return {url: page.url(), title: await page.title()}'
browser-control execute --session gap-ee-week1 'const p2=await context.newPage(); await p2.goto("http://127.0.0.1:8011/gap-ee/lessons/0002-refrigeration-cycle-and-cop.html", {waitUntil:"domcontentloaded"}); return {url: p2.url(), title: await p2.title()}'
# repeat for 0003, 0004, 0005 — each via context.newPage() in its own execute
browser-control execute --session gap-ee-week1 'const pages=context.pages(); return pages.map(p=>p.url())'
browser-control execute --session gap-ee-week1 'return await snapshot()'  # verify quiz widget: section.quiz exists
browser-control status --json | grep activeTargets  # should be 5 after week-1
```

Reuse `--session gap-ee-week1` for follow-ups; `await pages[0].bringToFront()` to focus.
Do not use `computer_use` for browser work — per user correction 2026-08-28, browser-control only.

## Verification evidence (2026-08-28)

- `curl -s 8011/gap-ee/lessons/0001...` -> 200, HTML contains `<title>0001 — Thermo…`
- `browser-control execute --session gap-ee-week1` on 0001-0005 each returned title
  `0001 — Thermo & Heat-Transfer Primer — gap-ee` through `0005 — TEA & LCOH…`
- `context.pages()` -> 5 urls, `status --json activeTargets:5`
- `snapshot()` on 0001 showed `gap-ee week 1, day 1` header and `section.quiz`
