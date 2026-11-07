# Chrome Stable — browse Setup

**browse (`@opencode/browse`, anomalyco/browse) is the default browser automation for this user.** It replaced browser-control on 2026-11-07. The built-in `browser` toolset (Browserbase/CDP) is disabled; browse's MCP server and CLI replace it. Runs on Chrome **Stable** (`C:\Program Files\Google\Chrome\Application\chrome.exe`).

## One-time setup

```bash
npm install --global @opencode/browse
browse settings set autoUpdate=notify   # updates only when the user agrees: `browse update`
```

- Extension: Chrome Web Store, id `mfnicocicmmlkpjnaffgihfjhdgjkdjg` (Developer: Anomaly). Chrome shows an Enhanced Safe Browsing "not trusted" warning for it (new publisher); the user approved installing anyway.
- Pairing: `browse pair` prints a one-time code; enter it on the extension's setup/options page and click Pair. `browse pair --list` shows paired browsers.
- Windows bug (0.0.13): `browse install` / `browse pair` fail with `spawnSync browse ENOENT` because they spawn `browse` without `.cmd`. Fix: set `"entry"` in `~/.config/browse/settings.json` to `C:\Users\<USER>\AppData\Roaming\npm\node_modules\@opencode\browse\dist\cli.mjs`.

## Hermes integration

Live config `%LOCALAPPDATA%\hermes\config.yaml` (not `~/.hermes/config.yaml`, which `browse install --agent hermes` would write):

```yaml
mcp_servers:
  browse:
    command: browse
    args:
    - mcp
    enabled: true
```

`hermes mcp test browse` lists its tools (execute, status, session_*, network, recording, flight_recorder, secrets_*, tabs_cleanup, settings). Skill: `browse` (top-level in the skills dir).

Verify:

```bash
browse doctor
browse execute --rm 'await page.goto("https://example.com"); return await page.title()'
```

## Relay and files

- Relay auto-starts on first command, `127.0.0.1:19988`. Data: `~/.config/browse`, `~/.local/share/browse`, logs in `~/.local/state/browse/logs`.
- Agent tabs open in the background in a collapsed group; idle tabs close after 10 minutes.
- Execute code has no `fs`/`require`: use `files.write(name, data)` / `files.read(path)` (temp dir and `OPENCODE_BROWSER_FILE_ROOTS` only, `;`-separated) and copy results into place from the shell.
- Scheduled job: cron "Linh Daily Log 8pm Reminder" runs `scripts/linh-daily-log-export.py` in session `gdrive-daily`; leave that session alone.

## Memory note

Chrome is a major memory consumer on 8GB systems — each tab can use 200-500MB. When the gateway is also running (~200MB), Chrome + Hermes Desktop + Claude Code can easily exceed 6-7GB, triggering OOM kills. See the OOM protection section in the parent skill.
