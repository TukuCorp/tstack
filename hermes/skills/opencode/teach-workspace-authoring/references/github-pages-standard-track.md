# GitHub Pages for standard track — private-repo 422 and file:// open (2026-08-30)

## Private-repo constraint (same as gap-ee)

- Repo `tah-allotrope/<PRIVATE_REPO>` is PRIVATE.
- `gh api repos/tah-allotrope/<PRIVATE_REPO> --jq '.private,.visibility,.has_pages'` → `true, PRIVATE, false`
- `gh api --method POST repos/tah-allotrope/<PRIVATE_REPO>/pages -f source.branch=main -f source.path=/`
  → `{"message":"Your current plan does not support GitHub Pages for this repository.","status":"422"}`
  (verified 2026-08-30 for both standard and gap-ee; free plan cannot host Pages from a private repo)
- `curl -I https://tah-allotrope.github.io/<PRIVATE_REPO>/` → `404 Not Found` until Pages is enabled.

## What week 2 did (2026-08-30)

- Authored standard-track lessons 0007 (signals & difference equations), 0008 (LTI poles), 0009 (graph shortest paths)
  as `teach-workspace/lessons/NNNN-slug.html` + `.md` companions, each with an *intended* github.io link in the meta:
  `https://tah-allotrope.github.io/<PRIVATE_REPO>/teach-workspace/lessons/NNNN-slug.html`
- Links are forward-references: they are present in HTML for sharing/bookmarking, but do not resolve until
  either (a) the main repo is made public and Pages enabled (`gh api .../pages -X POST ...`), or
  (b) a public slice repo is created (same pattern as `references/github-pages-week1.md` for gap-ee).
- Slice alternative for standard track if sharing before public: create `tah-allotrope/<PRIVATE_REPO>-week2`
  (or similar), push `lessons/0007-0009 + assets/style.css + assets/quiz.js + index.html`, enable Pages as above.

## Opening standard-track lessons locally

- Lessons use `../assets/style.css` and `../assets/quiz.js` with relative paths — `file://` DOES work for standard track
  (unlike gap-ee which needs http.server 8011). Relative asset loads succeed from `file://` on this browser.
- Working open on this Windows/MSYS host (where `explorer.exe` just opens Explorer, not the browser):
  `cmd.exe /c start "" "C:\Users\tukum\Downloads\<PRIVATE_REPO>\teach-workspace\lessons\0008-lti-poles-and-convergence.html"`
  (and similarly 0007, 0009). `cmd //c` (double-slash) is wrong on MSYS — use single-slash `/c`.
- To also probe the intended github.io URLs in the default browser:
  `cmd.exe /c start "" "https://tah-allotrope.github.io/<PRIVATE_REPO>/teach-workspace/lessons/0008-lti-poles-and-convergence.html"`
  — will 404 until Pages live, but confirms the link is well-formed.
- browser-control alternative (when browser-control is reachable):
  `browser-control execute 'await page.goto("file:///C:/Users/tukum/Downloads/<PRIVATE_REPO>/teach-workspace/lessons/0008-lti-poles-and-convergence.html")'`
  Do not use `browser_exec` cloud — it blocks private addresses and has no access to local `file://`.

## Verification

- `python teach-workspace/tools/verify_workspace.py teach-workspace` → `OK: 9 lessons, 2 records, 0 problems` after week 2.
- Standard-track git slice for week 2 push: `git add teach-workspace/lessons/0007* teach-workspace/lessons/0008* teach-workspace/lessons/0009* teach-workspace/LESSON-MAP.md teach-workspace/PROGRESS.md` → commit `teach: week 02 — 0007 ... 0008 ... 0009 ...` → `git push`.
