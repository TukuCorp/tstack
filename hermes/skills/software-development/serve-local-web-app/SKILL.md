---
name: serve-local-web-app
description: "Use when serving a web app locally: start, restart, get URL."
---

# Serving a local web app

Goal: give the user a working URL for the LATEST code of a web app (FastAPI/uvicorn, Node, etc.) running on their machine.

## Workflow

1. **Check for an existing listener first.** If the target port is already taken, a second server fails with a bind error (uvicorn: `[Errno 10048] ... only one usage of each socket address`). Find what's there:
   - `netstat -ano | grep -E ':8000\s' | grep LISTEN` → PID in last column
   - Identify it: `wmic process where "ProcessId=<pid>" get CommandLine,CreationDate,ExecutablePath /FORMAT:LIST`
2. **Stale-server check (critical).** A long-running server serves the code it loaded at startup — uvicorn/Node WITHOUT `--reload` does NOT pick up later commits. Compare:
   - Process CreationDate from wmic (format `YYYYMMDDHHMMSS...`)
   - Latest commit time: `git log -1 --format='%h %ci %s'`
   If the process started BEFORE the latest commits, it is stale → kill and restart. Killing a leftover dev server of the same repo is fine without asking, but say clearly in your reply that you did it.
3. **Start fresh in background:** `terminal(background=true, notify_on_complete=true)` using the repo venv python, e.g. `./.venv/Scripts/python.exe -m uvicorn <app> --factory --host 127.0.0.1 --port 8000`.
4. **Verify before reporting:** curl loop until 200: `for i in 1 2 3 4 5 6 7 8; do sleep 1; code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 5 http://127.0.0.1:8000/); echo "try $i: $code"; [ "$code" = "200" ] && break; done` — then hit the health endpoint too.
5. **Local vs public URL — never conflate.** Before promising a "latest version" URL, check whether a public deploy exists: README "Live URL:" section, render.yaml/vercel config, deploy plans with unchecked tasks. `curl -s -o /dev/null -w "%{http_code}" https://<app>.onrender.com` — 404 means never deployed. Report honestly: local URL serves latest code; a public URL requires dashboard/API access the agent does not have.

## Pitfalls (Windows git-bash / MSYS)

- `taskkill //PID <pid> //F` FAILS with "Invalid argument/option" — the double-slash MSYS trick does NOT work for taskkill/tasklist. Use SINGLE slash: `taskkill /PID <pid> /F`.
- `tasklist //FI "PID eq N"` fails the same way; use `wmic process where "ProcessId=N" get CommandLine,CreationDate,ExecutablePath /FORMAT:LIST` instead (keep the where-clause in double quotes).
- A background server that "exited (exit code 1)" with a 10048 bind error is NOT a crash — the port was taken. Diagnose the existing listener; don't retry blindly.
- `git -C <msys-path>` can fail with "cannot change to ... No such file or directory" even when the path exists — `cd <path> && git ...` is reliable.
- The health route name varies (`/health` vs `/api/health`) — read the server code or README before assuming.

## Static HTML / lesson viewing (no app server)

For plain HTML lessons (e.g. `<PRIVATE_REPO>/teach-workspace/gap-ee/lessons/*.html`), no
uvicorn/Node needed — serve the workspace root with the stdlib server:

```
python -m http.server 8011 --directory "C:/Users/tukum/Downloads/<PRIVATE_REPO>/teach-workspace"
# verify: curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8011/gap-ee/lessons/0001-thermo-and-heat-transfer-primer.html  # -> 200
```

Keep the same stale/occupied-port checks (step 1-2) — the http.server process also
holds the port and is stale if newer commits exist. Kill with `taskkill /PID <pid> /F`.

**Browser routing for localhost — hard pitfall.** `browser-control execute` (user's
local Chrome via relay 127.0.0.1:19989) reaches `http://127.0.0.1:<port>` fine.
`browser_exec` / cloud Browser-Use does NOT — it rejects private addresses:

```
Blocked: URL targets a private or internal address
```

For browser tasks on this machine the user's standing preference is browser-control
only — do not fall back to `computer_use` or cloud browser. Open lessons with
`browser-control session new <id>` + `context.newPage()` per lesson in one
execute block; reuse `--session <id>` for follows. See
`references/gap-ee-local.md` for the gap-ee week-1 URL list and multi-tab recipe.

## Verifying a page at a phone viewport (headless, no CDP)

`chrome --headless=new --dump-dom --window-size=390,844` does NOT lay out at 390:
the screenshot honours the window size but the DOM-dump viewport is clamped
(reports `innerWidth=758`), so any `overflow:0` / `cw==vw` assertion read from the
title is measured at the wrong width and passes vacuously. Measure the real
viewport by loading the page in a fixed-size iframe with file access allowed —
the iframe defines the layout width regardless of the window:

```html
<iframe id="f" src="file:///C:/path/page.html#A" style="width:390px;height:844px;border:0"></iframe>
<script>setTimeout(function(){
  var d=document.getElementById('f').contentDocument, w=document.getElementById('f').contentWindow;
  var over=[].slice.call(d.querySelectorAll('*')).filter(function(e){var r=e.getBoundingClientRect();
      return r.width>0 && (r.right>w.innerWidth+1 || r.bottom>w.innerHeight+1);});
  document.title='MEAS vw='+w.innerWidth+' scrollW='+d.documentElement.scrollWidth+' over='+over.length;
},8000);</script>
```

Run it with `--allow-file-access-from-files` (without it a `file://` iframe is an
opaque origin and `contentDocument` is null) and read the title from `--dump-dom`.
Assert `scrollWidth <= innerWidth+1`, zero overflowing elements, and — for touch
UI — every control's rect >= 44x44 with right/bottom >= 4 px inside the viewport.
This caught a real question (chips measured 48x44 at x=59..331, nothing clipped)
that an LLM reading the 390 px screenshot had answered wrongly; measure, don't
eyeball. Add the wrapper as a temp file and delete it — never modify the app page.

## Project-specific notes

- `references/carbonsim-online.md` — CarbonSim repo serve commands + deploy state.
- `references/gap-ee-local.md` — gap-ee static serving + browser-control localhost recipe
  (week 1 = 0001-0005, week 2 = 0006-0011, artifacts 0001-0003).
