# Helium (and Chrome Stable) — browse Setup

**browse (`@opencode/browse`, anomalyco/browse) is the default browser automation for this user.** It replaced browser-control on 2026-11-07. The built-in `browser` toolset (Browserbase/CDP) is disabled; browse's MCP server and CLI replace it. Since 2026-11-21 the daily browser is **Helium** (`%LOCALAPPDATA%\imput\Helium\Application\chrome.exe`, browse browser id `chrome-<TAILNET_MACHINE>-2`); Chrome Stable (`chrome-<TAILNET_MACHINE>`) stays paired as a fallback. Both show the same display name, so target Helium by id: MCP `session_new { browser: "chrome-<TAILNET_MACHINE>-2" }`. The CLI has no browser flag and uses the first connected browser.

Helium setup: the Web Store page may render blank, so copy the extension from Chrome's `User Data\Default\Extensions\mfnicocicmmlkpjnaffgihfjhdgjkdjg\<ver>` to `%LOCALAPPDATA%\imput\browse-ext`, delete `_metadata`, then in `helium://extensions` turn on Developer mode and Load unpacked (the manifest `key` keeps the ID). Pair by running `browse pair` and opening `chrome-extension://mfnicocicmmlkpjnaffgihfjhdgjkdjg/onboarding.html#code=<CODE>&port=19988` in Helium. The unpacked copy never auto-updates: recopy and click reload after a browse update.

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
- Scheduled job: cron "Linh Daily Log 8pm Reminder" runs `scripts/linh-daily-log-export.py` with `browse execute --rm` (one-shot session, tab closed afterward). Leave no standing browse sessions.

## Memory note

Chrome is a major memory consumer on 8GB systems — each tab can use 200-500MB. When the gateway is also running (~200MB), Chrome + Hermes Desktop + Claude Code can easily exceed 6-7GB, triggering OOM kills. See the OOM protection section in the parent skill.
