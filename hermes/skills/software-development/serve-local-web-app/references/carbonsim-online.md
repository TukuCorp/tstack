# CarbonSim Online — serve & deploy state

Repo: C:\Users\tukum\Downloads\carbonsim-online (branch master)

## Local serve

- Start: `./.venv/Scripts/python.exe -m uvicorn server.main:create_app --factory --host 127.0.0.1 --port 8000` (venv exists at repo root; fastapi/uvicorn verified)
- Port: 8000; health route: `/health` → `{"status":"ok"}` (NOT /api/health — render.yaml's healthCheckPath says /api/health but the live route is /health; check server/main.py before assuming)
- No build step; dev preview alternative: `python scripts/preview_run.py` (auto-picks next free port if 8000 busy)

## Deploy state (as of 2026-08-11)

- NO public URL. `render.yaml` (Render Blueprint, free tier, region oregon, branch master, autoDeploy, build=`pip install -r requirements.txt && pip install -e engine/`, start=`uvicorn server.main:create_app --factory --host 0.0.0.0 --port $PORT`) is committed and CI-verified, but the actual deploy was NEVER executed:
  - All tasks in `plans/2026-07-04-free-tier-deployment-plan.md` unchecked
  - README says "Live URL: TODO(deploy)"
  - `https://carbonsim-online.onrender.com` returns 404
- Real deploy requires interactive Render dashboard access (create Blueprint from repo, trigger first deploy) or a Render API key. Expected URL format: `https://carbonsim-online.onrender.com`.
- Caveats for when it deploys (from the plan): ~60s cold start after 15 min idle; SQLite state wiped on every restart/redeploy; single instance only (in-memory WS rooms in server/ws.py — no autoscaling); no auth — URL leak = anyone can play.

## Incident log

- 2026-08-09: a dev server left running from 09:52 was serving STALE code — 4 commits landed by 10:55 (facilitator dashboard d519047, seeded daily challenge 1010db4, requirements-dev.txt fix 47624db, final report 7765af6). Port 8000 appeared "live" (200 + health ok) but predated the latest code. Fix: compare wmic CreationDate vs `git log -1 --format='%ci'`, kill stale PID, restart, re-verify. Restart dev servers after pulls.
