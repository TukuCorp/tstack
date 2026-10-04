# gap-ee local serving — see serve-local-web-app/references/gap-ee-local.md

This is a mirror pointer for the teach-workspace-authoring skill. Canonical detail lives in
`serve-local-web-app/references/gap-ee-local.md` (http.server 8011, week 1 = 0001-0005,
browser-control localhost recipe, cloud Blocked: URL targets a private or internal address pitfall).

Short copy for this skill:

- Serve: `python -m http.server 8011 --directory "C:/Users/tukum/Downloads/<PRIVATE_REPO>/teach-workspace"`
- Week 1 URLs: 0001 thermo day1, 0002 refrigeration 1-2, 0003 steam 2-3, 0004 MEASUR 3-4, 0005 TEA 5
  at `http://127.0.0.1:8011/gap-ee/lessons/0001-...` through `0005-...`
- Open: `browser-control session new gap-ee-week1` + `context.newPage()` per lesson
  (not file://, not computer_use, not browser_exec cloud — blocked on 127.0.0.1)
- Verify: `snapshot()` shows gap-ee meta + quiz; `status --json activeTargets` == tab count

Full recipe + error transcript + verification evidence: read the canonical file above.
