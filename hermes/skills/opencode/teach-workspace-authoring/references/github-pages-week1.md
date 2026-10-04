# GitHub Pages for gap-ee week 1 — private-repo workaround (2026-08-28)

Private repo `tah-allotrope/<PRIVATE_REPO>` (visibility PRIVATE) cannot host Pages on free plan:

  gh api repos/tah-allotrope/<PRIVATE_REPO>/pages -X POST -f source[branch]=main -f source[path]=/
  -> {"message":"Your current plan does not support GitHub Pages for this repository.","status":"422"}

Public repos CAN host Pages on free plan. Workaround used 2026-08-28:

1. Create public repo `tah-allotrope/gap-ee-week1`:
   gh repo create tah-allotrope/gap-ee-week1 --public --description "gap-ee week1 lessons 0001-0005"

2. Push week 1 only (0001-0005 + assets) to main:
   /tmp/gap-ee-week1/
     index.html (week 1 landing with links to lessons/0001-0005)
     lessons/0001-thermo-and-heat-transfer-primer.html  (week 1 day1)
     lessons/0002-refrigeration-cycle-and-cop.html       (week 1 days 1-2)
     lessons/0003-steam-systems-fundamentals.html        (week 1 days 2-3)
     lessons/0004-measur-hands-on-steam-and-waste-heat.html (week 1 days 3-4)
     lessons/0005-tea-lcoh-fundamentals.html             (week 1 day5)
     assets/style.css, assets/quiz.js
   Note: lessons use ../assets/style.css — keep lessons/ + assets/ siblings so relative paths work.
   git add index.html lessons assets && git commit -m "gap-ee week1 0001-0005" && git push -u origin main

3. Enable Pages:
   gh api repos/tah-allotrope/gap-ee-week1/pages -X POST -f source[branch]=main -f source[path]=/
   -> {"html_url":"https://tah-allotrope.github.io/gap-ee-week1/","source":{"branch":"main","path":"/"},"public":true}
   Poll: gh api repos/tah-allotrope/gap-ee-week1/pages --jq .status
     building -> built (30-60s). Verify: curl -I https://tah-allotrope.github.io/gap-ee-week1/lessons/0001-...html -> 200 OK

4. Open via browser-control (not computer_use, not browser_exec cloud which blocks 127.0.0.1):
   browser-control session new gap-ee-github
   browser-control execute --session gap-ee-github 'await page.goto("https://tah-allotrope.github.io/gap-ee-week1/")'
   browser-control execute --session gap-ee-github 'const p2=await context.newPage(); await p2.goto("https://tah-allotrope.github.io/gap-ee-week1/lessons/0001-thermo-and-heat-transfer-primer.html")'
   ... repeat for 0002-0005 via context.newPage() in one execute block or sequential
   Verify: snapshot() shows headings, quiz li.q count, activeTargets == page count

Links (free github.io, shareable):
  https://tah-allotrope.github.io/gap-ee-week1/
  https://tah-allotrope.github.io/gap-ee-week1/lessons/0001-thermo-and-heat-transfer-primer.html
  https://tah-allotrope.github.io/gap-ee-week1/lessons/0002-refrigeration-cycle-and-cop.html
  https://tah-allotrope.github.io/gap-ee-week1/lessons/0003-steam-systems-fundamentals.html
  https://tah-allotrope.github.io/gap-ee-week1/lessons/0004-measur-hands-on-steam-and-waste-heat.html
  https://tah-allotrope.github.io/gap-ee-week1/lessons/0005-tea-lcoh-fundamentals.html

Pitfall: do not push whole teach-workspace (heavy MIT OCW PDFs); week 1 slice only. Keep repo public for free Pages.
See: gap-ee-local.md for localhost alternative (http.server 8011).
