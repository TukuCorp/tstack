# Chrome Stable — Browser Control Setup

**Browser Control (`@opencode-ai/browser-control`) is the default browser automation for this user.** The built-in `browser` toolset (Browserbase/CDP) is disabled; Browser Control's MCP server and CLI replace it. Runs on Chrome **Stable** (`C:\Program Files\Google\Chrome\Application\chrome.exe`) — Chrome Beta was uninstalled Aug 2026.

## One-time setup

```bash
# Install the package
npm install --global @opencode-ai/browser-control

# Load the unpacked extension in Chrome Stable:
# 1. Open chrome://extensions
# 2. Enable Developer mode
# 3. Load unpacked from:
#    C:\Users\tukum\AppData\Roaming\npm\node_modules\@opencode-ai\browser-control\extension\dist
# 4. Pin the Browser Control toolbar button
```

## Hermes integration

Set via `~/.hermes/config.yaml`:

```yaml
mcp_servers:
  browser-control:
    command: browser-control-mcp
skills:
  preload:
    - browser-control
```

- The `browser-control-mcp` MCP server registers 10 tools (execute, status, session_new, etc.) as native Hermes tools prefixed `mcp_browser_control_*`.
- The `browser-control` skill auto-loads on session start so the agent knows the workflow.
- The built-in `browser` toolset is disabled to avoid confusion.

Verify:

```bash
browser-control doctor
browser-control execute 'return { title: await page.title(), url: page.url() }'
browser-control execute --session <id> 'await page.goto("https://example.com"); return await snapshot()'
```

## Extension path

```
C:\Users\tukum\AppData\Roaming\npm\node_modules\@opencode-ai\browser-control\extension\dist
```

Key files: `manifest.json`, `background.js`, `content-script.js`, `offscreen.html`, `offscreen.js`

## Relay

Auto-starts on first `browser-control` command. Runs on `127.0.0.1:19989`. No need to start manually.

## Sessions

- Bare `execute` creates a fresh session. Continue with `--session <id>`.
- `await snapshot()` for compact DOM read. `await ariaSnapshot()` for deeper AX tree.
- `ref("e1").click()` to click by snapshot ref.
- `await handoff("message")` for CAPTCHA/2FA.
- Read-only: `browser-control session new <name> --read-only`
- Session journal at `~/.browser-control/sessions/<id>/journal.jsonl`

## Memory note

Chrome (Stable or Beta) is a major memory consumer on 8GB systems — each tab can use 200-500MB. When the gateway is also running (~200MB), Chrome + Hermes Desktop + Claude Code can easily exceed 6-7GB, triggering OOM kills. See the OOM protection section in the parent skill.
